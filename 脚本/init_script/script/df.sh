#!/bin/bash
ansible-playbook /etc/ansible/playbook/df_elk.yml -e host=es

echo "`date +%Y%m%d-%T` `cat /root/192.168.1.47/root/ip.txt /root/192.168.1.47/root/df.txt`" | awk '{tmp=$0;getline;print tmp","$0}'>> /root/info.txt
echo "`date +%Y%m%d-%T` `cat /root/192.168.2.31/root/ip.txt /root/192.168.2.31/root/df.txt`" | awk '{tmp=$0;getline;print tmp","$0}'>> /root/info.txt
echo "`date +%Y%m%d-%T` `cat /root/192.168.2.32/root/ip.txt /root/192.168.2.32/root/df.txt`" | awk '{tmp=$0;getline;print tmp","$0}'>> /root/info.txt
rm -rf /root/192.168.*
