ARG BUILD_FROM
FROM $BUILD_FROM

# Copy data for add-on
COPY rootfs /

# Install bluetti_mqtt
RUN apk add --update --no-cache \
		bluez \
		git \
	&& pip install git+https://github.com/ftrueck/bluetti_mqtt.git@aa66d850ca2252ccce885aaeda71ea146f019845 \
	&& apk del git \
	&& rm -rf /var/cache/apk/* /lib/apk/db/* \
	&& chmod a+x /run.sh

CMD [ "/run.sh" ]
