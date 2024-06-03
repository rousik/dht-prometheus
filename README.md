# Summary

This is lightweight software stack for collecting variety of environmental data via sensors connected to Raspberry Pi (Zero 2 W) and exposing these as prometheus metrics that can then be scraped by prometheus and visualized in grafana. This entire stack is running on the said raspberry device, but could be linked to larger array of devices if needed.

## Hardware wiring

'm using DHT22 sensor for temperature and humidity, and MH-Z19 for CO2 monitoring.

The default values in the code assume the following wiring:
* DHT-22 - connected to pins 1 (3v), 7 (GPIO 7) and 9 (Gnd).
* MH-Z19 - connected via serial port, on pins 4 (5v) , 6 (Gnd) , 8 (TxD) and 10 (RxD), with Tx/Rx cross-wired with the sensor pins (Tx on the sensor hooks to Rx on Raspberry and vice versa) 

