#!/bin/bash

OPENVPN_DIR=/etc/openvpn
OPENVPN_NEED=/usr/local/bin/

if [ ! -f ${OPENVPN_DIR}/server/server.crt ]
then
    echo 'openvpn initializing ...'
    # make server ca and server crt
    cd ${OPENVPN_DIR}
    mkdir -p server client logs
    cd /root/
    mkdir -p openvpn-ca client-configs
    cp /usr/share/easy-rsa/* openvpn-ca
    cp ${OPENVPN_NEED}/make_cert.sh ${OPENVPN_NEED}/vars openvpn-ca
    cp openvpn-ca/openssl-1.0.0.cnf openvpn-ca/openssl.cnf
    cd openvpn-ca
    ./make_cert.sh
    cd ./keys
    cp ca.crt server.crt server.key dh* ${OPENVPN_DIR}/server/
    cp ${OPENVPN_NEED}/server.conf ${OPENVPN_DIR}
    cp ${OPENVPN_NEED}/check_password.sh ${OPENVPN_DIR}/server/
    sed -i "s|^dh.*|dh ${OPENVPN_DIR}/server/dh${KEY_SIZE}.pem|" ${OPENVPN_DIR}/server.conf

    touch ${OPENVPN_DIR}/password
    chmod 600 ${OPENVPN_DIR}/password
    touch ${OPENVPN_DIR}/logs/password.log
    chmod 644 ${OPENVPN_DIR}/logs/password.log

    # make client crt
    cd /root/
    cp ${OPENVPN_NEED}/make_config.sh ${OPENVPN_NEED}/base.conf client-configs
    ./client-configs/make_config.sh client

    rm -rf /usr/local/bin/*
    rm -rf /root/client-configs /root/openvpn-ca
else
    echo 'openvpn has been initialized, skip.'
fi

if [ ! -c /dev/net/tun ]
then
    echo "creating /dev/net/tun"
    mkdir /dev/net
    mknod /dev/net/tun c 10 200
fi

# fill environment variable in
sed -i "s|^server.*|server ${SERVER}|" ${OPENVPN_DIR}/server.conf
sed -i "s|^push \"route.*|push \"route ${PUSH}\"|" ${OPENVPN_DIR}/server.conf
sed -i "s|^remote.*|remote ${CLIENTREMOTE} 1194|" ${OPENVPN_DIR}/client/client.ovpn
