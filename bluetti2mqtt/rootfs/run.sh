#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: Bluetti2MQTT
# MQTT bridge between Bluetti and Home Assistant
# ==============================================================================

bashio::log.info 'Reading configuration settings...'

MODE=$(bashio::config 'mode')
HA_CONFIG=$(bashio::config 'ha_config')
BT_MAC=$(bashio::config 'bt_mac')
POLL_SEC=$(bashio::config 'poll_sec')
SCAN=$(bashio::config 'scan')

# Setup MQTT Auto-Configuration if values are not set.
if bashio::config.has_value 'mqtt_host'; then
	MQTT_HOST=$(bashio::config 'mqtt_host')
else
	MQTT_HOST=$(bashio::services "mqtt" "host")
fi

if bashio::config.has_value 'mqtt_port'; then
	MQTT_PORT=$(bashio::config 'mqtt_port')
else
	MQTT_PORT=$(bashio::services "mqtt" "port")
fi

if bashio::config.has_value 'mqtt_username'; then
	MQTT_USERNAME=$(bashio::config 'mqtt_username')
else
	MQTT_USERNAME=$(bashio::services mqtt "username")
fi

if bashio::config.has_value 'mqtt_password'; then
	MQTT_PASSWORD=$(bashio::config 'mqtt_password')
else
	MQTT_PASSWORD=$(bashio::services "mqtt" "password")
fi

if [ $(bashio::config 'debug') == true ]; then
	export DEBUG=true
	bashio::log.info 'Debug mode is enabled.'
fi

args=()
if [ ${SCAN} == true ]; then
	args+=(--scan)
fi

case $MODE in

	mqtt)
		bashio::log.info 'Starting bluetti-mqtt...'
		args+=( \
			--broker ${MQTT_HOST} \
			--port ${MQTT_PORT} \
			--username ${MQTT_USERNAME} \
			--password ${MQTT_PASSWORD} \
			--interval ${POLL_SEC} \
			--ha-config ${HA_CONFIG} \
			${BT_MAC})
		bluetti-mqtt ${args[@]}
		;;

	discovery)
		bashio::log.info 'Starting bluetti-discovery...'
		bashio::log.info 'Messages are NOT published to the MQTT broker in discovery mode.'
		mkdir -p /share/bluetti2mqtt/
		args+=( \
			--log /share/bluetti2mqtt/discovery_$(date "+%m%d%y%H%M%S").log \
			${BT_MAC})
		bluetti-discovery ${args[@]}
		;;

	logger)
		bashio::log.info 'Starting bluetti-logger...'
		bashio::log.info 'Messages are NOT published to the MQTT broker in logger mode.'
		mkdir -p /share/bluetti2mqtt/
		args+=( \
			--log /share/bluetti2mqtt/logger_$(date "+%m%d%y%H%M%S").log \
			${BT_MAC})
		bluetti-logger ${args[@]}
		;;

	*)
		bashio::log.warning "No mode selected!  Please choose either 'mqtt', 'discovery', or 'logger'."
		;;

esac
