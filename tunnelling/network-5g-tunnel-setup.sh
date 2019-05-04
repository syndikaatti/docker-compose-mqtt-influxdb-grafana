#!/bin/sh

FOU_REMOTE_PORT=8001
FOU_REMOTE_IP=195.148.127.95

FOU_LOCAL_PORT=1883
FOU_LOCAL_IP=195.148.126.105

FOU_REMOTE_NETWORK="10.200.1.1/24"

set -e

# Configure the UDP port for incoming tunnelled IP packets
modprobe fou
ip fou add port $FOU_LOCAL_PORT ipproto 4

# Configure a tunnel for outgoing tunnelled IP packets
ip link add name fou0 type ipip \
	 remote $FOU_REMOTE_IP local $FOU_LOCAL_IP \
	 encap fou encap-sport $FOU_LOCAL_PORT encap-dport $FOU_REMOTE_PORT encap-csum \
	 dev eth0

ip link set up dev tunl0
ip link set up dev fou0
ip addr add 10.200.1.1/24 dev fou0
