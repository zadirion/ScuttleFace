#!/bin/sh
sudo ip link add eth0.70 link eth0 type macvlan mode bridge
sudo ip addr add 192.168.2.10/24 dev eth0.70
sudo ifconfig eth0.70 up


sudo ip link add mymacvlan70 link eth0.70 type macvlan mode bridge
sudo ip addr add 192.168.2.10/24 dev mymacvlan70
sudo ifconfig mymacvlan70 up

docker network create -d macvlan \
	--subnet=192.168.0.0/16 \
	--ip-range=192.168.2.0/24 \
	-o macvlan_mode=bridge \
	-o parent=eth0.70 fbrelaynet