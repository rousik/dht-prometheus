import time

import adafruit_dht
import board
from prometheus_client import Counter, Gauge, start_http_server

TEMPERATURE = Gauge("temperature", "Temperature in Celsius")
HUMIDITY = Gauge("humidity", "Relative humidity in %")
ERRORS = Counter("dht_read_errors", "Number of errors while reading the sensor")

if __name__ == "__main__":
    start_http_server(8000)
    # TODO(rousik): add options for different wiring and for multiple sensors.
    dhtDevice = adafruit_dht.DHT22(board.D4)
    while True:
        try:
            TEMPERATURE.set(dhtDevice.temperature)
            HUMIDITY.set(dhtDevice.humidity)

            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity
            print("Temp: {:.1f} C    Humidity: {}% ".format(temperature_c, humidity))
        except RuntimeError as error:
            print(error.args[0])
            ERRORS.inc()
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error
        # TODO(rousik): do we want to control the collection frequency?
        time.sleep(1.0)