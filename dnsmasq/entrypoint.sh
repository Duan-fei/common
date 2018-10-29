#!/bin/bash

case "$1" in
    dnsmasq)
        if [ ! -f /etc/dnsmasq/dnsmasq.conf ]
        then
            echo "initializing dnsmasq"
            mkdir -p /etc/dnsmasq/logs
            cp /root/dnsmasq_need/dnsmasq.hosts  /etc/dnsmasq/
            cp /root/dnsmasq_need/dnsmasq.resolv /etc/dnsmasq/
            cp /root/dnsmasq_need/dnsmasq.conf   /etc/dnsmasq/
            echo "initialize dnsmasq done"
        fi

        exec dnsmasq -k ${@:2}
        ;;
    *)
        exec $@
        ;;
esac
