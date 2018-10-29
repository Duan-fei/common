FROM registry.cn-beijing.aliyuncs.com/shannonai/debian

# runtime dependencies
RUN apt-get update && apt-get install -yqq --no-install-recommends dnsmasq \
        && rm -rf /var/lib/apt/lists/* \
        && mkdir -p /etc/dnsmasq/logs

COPY entrypoint.sh /root/
COPY dnsmasq_need /root/dnsmasq_need

RUN chmod u+x /root/entrypoint.sh

VOLUME /etc/dnsmasq

EXPOSE 53
WORKDIR /root/
ENTRYPOINT ["/root/entrypoint.sh"]
CMD ["dnsmasq", "-C", "/etc/dnsmasq/dnsmasq.conf"]
