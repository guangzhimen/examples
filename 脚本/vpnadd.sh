#!/bin/bash
#
#ip add
gw=`echo $1 |awk -vFS="." '{print $3}'`
check_dev=`ip add |grep $2 |grep UP |wc -l`
intercheck=`echo $2 | grep -c '^e[a-z]'`
ipcheck=`echo $1 | grep -c '^[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}$'`
vpn_inter=`ifconfig |grep $2:3 |wc -l`
vpn_route1=`route |grep 192.168.1.0 |wc -l`
vpn_route2=`route |grep 192.168.2.0 |wc -l`
vpn_route3=`route |grep 192.168.3.0 |wc -l`
while :
do
	if [ ${intercheck} -eq 1 ] && [ ${ipcheck} -eq 1 ]; then
		break
	else
		echo "You input error!"
		echo "The correct format is: vpnadd.sh [the vpn ip] [network interface]"
		exit
	fi
done
while :
do	
	if [ ${check_dev} -eq 1 ]; then
		break
	else
		echo "You input a interface not found!"
		exit
	fi	
done
if [ ${vpn_inter} -eq 0 ]; then
	ifconfig $2:3 $1 netmask 255.255.255.0 up
fi
if [ ${vpn_route1} -eq 0 ]; then
	route add -net 192.168.1.0 netmask 255.255.255.0 gw 10.10.${gw}.1
fi
if [ ${vpn_route2} -eq 0 ]; then
	route add -net 192.168.2.0 netmask 255.255.255.0 gw 10.10.${gw}.1
fi
if [ ${vpn_route3} -eq 0 ]; then
	route add -net 192.168.3.0 netmask 255.255.255.0 gw 10.10.${gw}.1
fi
cat << EOF > /etc/sysconfig/network-scripts/ifcfg-$2:3
TYPE=Ethernet
BOOTPROTO=none
IPADDR=$1
NETMASK=255.255.255.0
NAME=$2:3
DEVICE=$2:3
ONBOOT=yes
EOF
cat << EOA > /etc/sysconfig/network-scripts/route-$2
192.168.1.0/24 via 10.10.${gw}.1
192.168.2.0/24 via 10.10.${gw}.1
192.168.3.0/24 via 10.10.${gw}.1
EOA

del_inter=`cat /etc/rc.d/rc.local |grep ifconfig |wc -l`
del_route=`cat /etc/rc.d/rc.local | grep 10.10.141.0 |wc -l`

if [ ${del_inter} -eq 1 ]; then
	sed -i '/^ifconfig/d' /etc/rc.d/rc.local
fi
if [ ${del_route} -eq 1 ]; then
	sed -i '/^route add -net 10.10.141.0/d' /etc/rc.d/rc.local
fi

ping 192.168.3.23