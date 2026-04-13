#!/bin/bash
export PATH=$PATH:/sbin

apt install frr frr-pythontools -y
cp frr/frr.conf /etc/frr/frr.conf
cp frr/daemons /etc/frr/daemons
systemctl reload frr
apt install tcpdump -y
apt install nodejs npm -y
anpm install -g allure-commandline -y
apt install default-jre -y

ip -all netns delete

ip netns add r1
ip netns add r2

ip link add veth-r1-input type veth peer name input
ip link set veth-r1-input netns r1
ip netns exec r1 ip link set veth-r1-input up
ip link set input up
ip netns exec r1 ip addr add 10.0.1.1/24 dev veth-r1-input

ip link add veth-r1-l2 type veth peer name output1
ip link set veth-r1-l2 netns r1
ip netns exec r1 ip link set veth-r1-l2 up
ip link set output1 netns r2
ip netns exec r2 ip link set output1 up
ip netns exec r1 ip addr add 10.1.1.1/24 dev veth-r1-l2
ip netns exec r2 ip addr add 10.1.1.2/24 dev output1

ip link add veth-r1-l3 type veth peer name output2
ip link set veth-r1-l3 netns r1
ip netns exec r1 ip link set veth-r1-l3 up
ip link set output2 netns r2
ip netns exec r2 ip link set output2 up
ip netns exec r1 ip addr add 10.2.1.1/24 dev veth-r1-l3
ip netns exec r2 ip addr add 10.2.1.2/24 dev output2

ip link add veth-r1-l4 type veth peer name output3
ip link set veth-r1-l4 netns r1
ip netns exec r1 ip link set veth-r1-l4 up
ip link set output3 netns r2
ip netns exec r2 ip link set output3 up
ip netns exec r1 ip addr add 10.3.1.1/24 dev veth-r1-l4
ip netns exec r2 ip addr add 10.3.1.2/24 dev output3

ip netns exec r1 ip link set lo up
ip netns exec r2 ip link set lo up

ip netns exec r2 ip addr add 172.172.174.1/24 dev lo

############################################################
# uncomment if linux core version >= 5.14
#ip netns exec r1 sysctl -w net/ipv4/fib_multipath_hash_policy=3
#ip netns exec r2 sysctl -w net/ipv4/fib_multipath_hash_policy=3
#ip netns exec r1 sysctl -w net.ipv4.fib_multipath_hash_fields=1
#ip netns exec r2 sysctl -w net.ipv4.fib_multipath_hash_fields=1

############################################################
# uncomment if linux core version < 5.14
ip netns exec r1 sysctl -w net/ipv4/fib_multipath_hash_policy=0
ip netns exec r2 sysctl -w net/ipv4/fib_multipath_hash_policy=0


sysctl -w net.ipv4.ip_forward=1
ip netns exec r1 sysctl -w net.ipv4.ip_forward=1
ip netns exec r2 sysctl -w net.ipv4.ip_forward=1

ip netns exec r1 sysctl -w net.ipv4.conf.lo.rp_filter=0
ip netns exec r1 sysctl -w net.ipv4.conf.veth-r1-input.rp_filter=0
ip netns exec r1 sysctl -w net.ipv4.conf.veth-r1-l2.rp_filter=0
ip netns exec r1 sysctl -w net.ipv4.conf.veth-r1-l3.rp_filter=0
ip netns exec r1 sysctl -w net.ipv4.conf.veth-r1-l4.rp_filter=0
ip netns exec r2 sysctl -w net.ipv4.conf.lo.rp_filter=0
ip netns exec r2 sysctl -w net.ipv4.conf.output1.rp_filter=0
ip netns exec r2 sysctl -w net.ipv4.conf.output2.rp_filter=0
ip netns exec r2 sysctl -w net.ipv4.conf.output3.rp_filter=0
