#!/bin/bash
inter=`ip add |grep " UP" |awk -F": " '{print $2}'`
inter_sum=`ip add |grep " UP" |awk -F": " '{print $2}' |wc -l`

message() {
while :
do
	read -p "please enter the IP address: " ip
        ipcheck=`echo ${ip} | grep -c ''`
        if [ $ipcheck -eq 1 ]
        then
                break
        fi
        echo ""
        echo "You have not input a valid IP Address!"
done
while :
do
	read -p "please enter the NETMASK address: " netmask
        maskcheck=`echo ${netmask} | grep -c '^[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}$'`
        if [ $maskcheck -eq 1 ]
        then
                break
        fi
        echo ""
        echo "You have not input a valid NETMASK Address!"
done
while :
do
	read -p "please enter the GATEWAY address: " gateway
        gatewaycheck=`echo ${gateway} | grep -c '^[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}$'`
        if [ $gatewaycheck -eq 1 ]
        then
                break
        fi
        echo ""
        echo "You have not input a valid GATEWAY Address!"
done
}

if [ ${inter_sum} -eq 1 ]; then
	message

cat << EOF > /etc/sysconfig/network-scripts/ifcfg-$inter
TYPE=Ethernet
BOOTPROTO=none
IPADDR=$ip
NETMASK=$netmask
GATEWAY=$gateway
NAME=$inter
DEVICE=$inter
ONBOOT=yes
DNS1=223.5.5.5
EOF

else
	message
	echo -e "\033[31m######   Network Message   #######\033[0m"
	ip addr
	read -p "please enter the INTERFACE address: " shi

cat << EOF > /etc/sysconfig/network-scripts/ifcfg-$shi
TYPE=Ethernet
BOOTPROTO=none
IPADDR=$ip
NETMASK=$netmask
GATEWAY=$gateway
NAME=$shi
DEVICE=$shi
ONBOOT=yes
DNS1=223.5.5.5
EOF
fi
sleep 1
/etc/init.d/network restart
