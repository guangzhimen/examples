#!/bin/bash
#
path=`pwd`
for ip in `cat ${path}/server.csv |awk -F"," 'NR>1 {print $1}'`
do
    zabbix_server=`awk -F"," -v i="${ip}" '{if(i==$1)print $6}' ${path}/server.csv`
    ntp_server=`awk -F"," -v i="${ip}" '{if(i==$1)print $7}' ${path}/server.csv`
    ansible-playbook `pwd`/bin/initialization.yml -e "host=${ip} zabbix=${zabbix_server} ntp=${ntp_server}"
done
