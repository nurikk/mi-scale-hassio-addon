ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

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
