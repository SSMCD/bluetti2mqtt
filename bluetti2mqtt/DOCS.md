# Bluetti2MQTT

MQTT bridge between Bluetti and Home Assistant.

This is a simple Home Assistant add-on for [bluetti_mqtt](https://github.com/warhammerkid/bluetti_mqtt).

This add-on was created as an easy method to get Bluetti data into Home Assistant, without having to setup [bluetti_mqtt](https://github.com/warhammerkid/bluetti_mqtt) on a separate device.

___

## Configuration

### Optional: `mqtt_host`

> The MQTT host.  Leave blank if you are using the Mosquitto broker add-on.

### Optional: `mqtt_port`

> The MQTT port.  Leave blank if you are using the Mosquitto broker add-on.

### Optional: `mqtt_username`

> The MQTT username.  Leave blank if you are using the Mosquitto broker add-on.

### Optional: `mqtt_password`

> The MQTT password.  Leave blank if you are using the Mosquitto broker add-on.

### Required: `bt_mac`

> The MAC address(es) of the Bluetti devices.  Separate multiple addresses with a single space.

### Required: `poll_sec`

> Polling interval in seconds.

### Required: `ha_config`

> What fields to configure in Home Assistant - defaults to most fields ("normal")

### Required: `scan`

> Enable to scan for nearby devices and display the resulting mac addresses in the log tab.  Copy the address(es) from the log and paste into the corresponding field in the Configuration tab.

### Required: `debug`

> Enable debug mode.  Check the log tab for output.

### Required: `log`

> Enable to start the program in log mode.  Logs are saved to /share/bluetti2mqtt/device.log.
> NOTE:  In log mode, no data will be published to the MQTT broker.  This runs the bluetti-logger command as described in the link above.

___

If all goes well, something like the following will be output to the log tab:

```
INFO: Reading configuration settings...
INFO: Starting bluetti-mqtt...
INFO     Connecting to MQTT broker...
INFO     Starting to poll clients...
INFO     Connecting to clients: ['00:11:22:33:44:55']
INFO     Connected to MQTT broker
INFO     Sent discovery message of XXXXX-0000000000000 to Home Assistant
INFO     Connected to device: 00:11:22:33:44:55
```
___