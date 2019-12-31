ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

# adjust here the environment variables
ENV MISCALE_MAC 00:00:00:00:00:00
ENV MQTT_PREFIX miScale
ENV MQTT_HOST 192.168.1.3
ENV MQTT_USERNAME username
ENV MQTT_PASSWORD password
ENV MQTT_PORT 1883
ENV MQTT_TIMEOUT 30
ENV USER1_GT 80
ENV USER1_SEX male
ENV USER1_NAME Tobias
ENV USER1_HEIGHT 186
ENV USER1_DOB 1990-01-01
ENV USER2_LT 70
ENV USER2_SEX female
ENV USER2_NAME Juliane
ENV USER2_HEIGHT 173
ENV USER2_DOB 1990-01-01

WORKDIR /opt/miscale
COPY src /opt/miscale

RUN apk update && \
    apk add --no-cache \
        python3 \
        dcron \
        bash \
        bash-doc \
        bash-completion \
        tar \
        linux-headers \
        gcc \
        make \
        glib-dev \
        alpine-sdk \
    && rm -rf /var/cache/apk/*

RUN pip3 install -r requirements.txt

RUN mkdir -p /var/log/cron \
    && mkdir -m 0644 -p /var/spool/cron/crontabs \
    && touch /var/log/cron/cron.log \
    && mkdir -m 0644 -p /etc/cron.d && \
    echo -e "*/5 * * * * python3 /opt/miscale/Xiaomi_Scale.py\n" >> /var/spool/cron/crontabs/root

## Cleanup
RUN apk del alpine-sdk gcc make tar

# Copy in docker scripts to root of container... (cron won't run unless it's run under bash/ash shell)
COPY dockerscripts/ /

RUN chmod a+x /entrypoint.sh
RUN chmod a+x /cmd.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/cmd.sh"]
