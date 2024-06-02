import time

import struct
import serial
import adafruit_dht
import board
from prometheus_client import Counter, Gauge, start_http_server


class TempAndHumiditySensor:
    def __init__(self, pin=board.D7, sensor_name=""):
        self._device = adafruit_dht.DHT22(pin)
        self._temp_c = Gauge(sensor_name + "temperature_c", "Temperature in Celsius")
        self._temp_f = Gauge(sensor_name + "temperature_f", "Temperature in Fahrenheit")
        self._humidity = Gauge(sensor_name + "humidity", "Relative humidity in %")
        self._read_errors = Counter(sensor_name + "dht22_read_errors", "Number of errors while reading the sensor value")

    def refresh(self) -> bool:
        """Refreshes the sensor values; returns True upon success, False if the operation failed."""
        try:
            temp_c = self._device.temperature
            humidity = self._device.humidity
            self._temp_c.set(temp_c)
            self._temp_f.set(temp_c * 1.8 + 32)
            self._humidity.set(humidity)
            return True
        except RuntimeError as error:
            self._read_erors.inc()
            return False


class CarbonSensor:
    """Reads co2 values from MH-Z19 CO2 sensor over serial port (Tx, Rx pins)"""
    # This is reduction and adaptation of the code from:
    # https://github.com/UedaTakeyuki/mh-z19/blob/master/mh_z19.py
    def __init__(self, tty="/dev/ttyS0"):
        self._serial = serial.Serial(
            tty,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1.0
        )
        self._co2_concentration = Gauge("co2_ppm", "CO2 ppm concenctration")
        self._read_errors = Counter("mh_z19_read_errors", "Read errors for the co2 mh-z19 sensor")


    def _valid_response(self, resp_bytes) -> bool:
        """Returns true if the response is valid."""
        if len(resp_bytes) < 4:  # Response long enough
            return False
        if resp_bytes[0] != 0xff or resp_bytes[1] != 0x86:  # Header correct
            return False
        # If I'm reading the code right, we simply sum up bytes from [1:-1]
        # modulo 256 (single byte checksum) and then if we add this with the last
        # element, resp_bytes[-1], we should get zero modulo 256
        if (sum(resp_bytes[1:-1]) % 256 + resp_bytes[-1]) % 256 == 0:
            return True
        else:
            cs = struct.pack('B', sum(resp_bytes[1:-1]) % 256)
            cs_valid = resp_bytes[-1]
            print(f"I may have gotten the checksum logic wrong! {cs} {cs_valid}")
            return False

    def refresh(self):
        # TODO(rousik): retry this few times if needed.
        try:
            self._serial.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")
            result = self._serial.read(9)
            if self._valid_response(result):
                co2_ppm = result[2]*256 + result[3]
                self._co2_concentration.set(co2_ppm)
            else:
                self._read_errors.inc()
        except RuntimeError as error:
            self._read_errors.inc()

    
def main():
    start_http_server(8000)
    # TODO(rousik): add options for different wiring and for multiple sensors.
    dht22 = TempAndHumiditySensor()
    mhz19 = CarbonSensor()

    while True:
        dht22.refresh()
        mhz19.refresh()
        time.sleep(1.0)


if __name__ == "__main__":
    main()
