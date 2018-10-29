#!/bin/bash
echo -e "-------make_cert.sh start--------\n\n"

source vars
./clean-all

echo -e "\n\n----------build-ca-----------"
/usr/bin/expect << EOF
spawn ./build-ca
expect "Country Name" {send "\r"}
expect "State or Province Name" {send "\r"}
expect "Locality Name" {send "\r"}
expect "Organization Name" {send "\r"}
expect "Organizational Unit Name" {send "\r"}
expect "Common Name" {send "\r"}
expect "Name" {send "\r"}
expect "Email Address" {send "\r"}
expect eof
EOF

echo -e "\n\n-------build-key-server-------"

/usr/bin/expect << EOF
spawn ./build-key-server server
expect "Country Name" {send "\r"}
expect "State or Province Name" {send "\r"}
expect "Locality Name" {send "\r"}
expect "Organization Name" {send "\r"}
expect "Organizational Unit Name" {send "\r"}
expect "Common Name" {send "\r"}
expect "Name" {send "\r"}
expect "Email Address" {send "\r"}
expect "A challenge password" {send "\r"}
expect "An optional company name" {send "\r"}
expect "Sign the certificate?" {send "y\r"}
expect "commit?" {send "y\r"}
expect eof
EOF

echo -e "\n\n--------build-dh-----------"

./build-dh

echo -e "\n\n-------make_cert.sh done--------"
