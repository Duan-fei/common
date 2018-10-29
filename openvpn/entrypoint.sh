#!/bin/bash

case "$1" in
  openvpn)
    /root/openvpn_init.sh
    exec openvpn --dev tun --config /etc/openvpn/server.conf ${@:2}
  ;;
  *)
    exec "$@"
  ;;
esac
