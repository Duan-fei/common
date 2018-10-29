#!/bin/bash
# rgument: Client identifier

KEY_DIR=/root/openvpn-ca/keys
OUTPUT_DIR=/etc/openvpn/client
BASE_CONFIG=/root/client-configs/base.conf

cat ${BASE_CONFIG} \
        <(echo -e '<ca>') \
        ${KEY_DIR}/ca.crt \
        <(echo -e '</ca>') \
        > ${OUTPUT_DIR}/${1}.ovpn

