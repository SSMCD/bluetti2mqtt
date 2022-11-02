ARG BUILD_FROM
FROM $BUILD_FROM
COPY rootfs /
RUN pip install bluetti_mqtt
CMD ["/run.sh"]