FROM registry.cn-beijing.aliyuncs.com/shannonai/debian

# runtime dependencies
RUN set -ex \
    && apt-get -yqq update && apt-get install -yqq --no-install-recommends \
        openvpn=2.4.0-6+deb9u2 \
        expect \
        easy-rsa \
    && rm -rf /var/lib/apt/lists/* 

VOLUME /etc/openvpn
EXPOSE 1194

COPY openvpn_init.sh /root/
COPY entrypoint.sh /root/
COPY openvpn_need/ /usr/local/bin/

ENTRYPOINT ["/root/entrypoint.sh"]
CMD ["openvpn"]
