#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: Bluetti2MQTT
# MQTT bridge between Bluetti and Home Assistant
# ==============================================================================

bashio::log.info 'Reading configuration settings...'

if bashio::config.has_value 'mqtt_username'; then
	MQTT_USERNAME=$(bashio::config 'mqtt_username')
fi

if bashio::config.has_value 'mqtt_password'; then
	MQTT_PASSWORD=$(bashio::config 'mqtt_password')
fi

if bashio::config.has_value 'mqtt_host'; then
	MQTT_HOST=$(bashio::config 'mqtt_host')
fi

if bashio::config.has_value 'bt_mac'; then
	BT_MAC=$(bashio::config 'bt_mac')
fi

if bashio::config.has_value 'poll_sec'; then
	POLL_SEC=$(bashio::config 'poll_sec')
fi

if [ $(bashio::config 'scan') == true ]; then
	bluetti-mqtt --scan
fi

if [ $(bashio::config 'debug') == true ]; then
	export DEBUG=true
fi

if [ $(bashio::config 'log') == true ]; then
	bashio::log.info 'Starting in log mode...'
	mkdir -p /share/bluetti2mqtt/
	bluetti-logger --log /share/bluetti2mqtt/device_$(date "+%m%d%y%H%M%S").log ${BT_MAC}
else
	bluetti-mqtt --broker ${MQTT_HOST} --username ${MQTT_USERNAME} --password ${MQTT_PASSWORD} --interval ${POLL_SEC} ${BT_MAC}
fi
