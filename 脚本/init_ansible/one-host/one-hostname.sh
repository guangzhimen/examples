#!/bin/bash
##ip=$1
###host=$2
read -p "input server ip: " ip
read -p "input server host: " host
ansible ${ip} -m shell -a "echo ${host} > /etc/hostname"
