ARG BUILD_FROM
FROM $BUILD_FROM

# Copy data for add-on
COPY rootfs /

# Install bluetti_mqtt
RUN pip install bluetti-mqtt==0.11.1

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
