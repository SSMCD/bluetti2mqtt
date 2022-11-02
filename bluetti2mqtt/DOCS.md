# Bluetti to MQTT

MQTT bridge between Bluetti and Home Assistant.

This addon installs and runs the python-based interface fround here: https://github.com/warhammerkid/bluetti_mqtt

Before starting the addon, you will need to input your MQTT broker info and Bluetti device info into the Configuration tab.

If scan mode is enabled, the program will scan for nearby devices and display the resulting mac addresses in the log tab.  Copy the address(es) from the log and paste into the corresponding field in the Configuration tab.

If log mode is enabled, the program will log the raw data to your /share directory.