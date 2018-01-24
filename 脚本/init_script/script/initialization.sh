#!/bin/bash
source /etc/profile
sed -i '/^Server=/c Server=192.168.1.12' /apps/usr/zabbix/etc/zabbix_agentd.conf
sed -i '/^ServerActive=/c ServerActive=192.168.1.12' /apps/usr/zabbix/etc/zabbix_agentd.conf
/etc/init.d/zabbix_agentd start
sed -i '/10.10.10.10/d' /var/spool/cron/root
echo '0 1 * * * ( /usr/sbin/ntpdate 192.168.1.1  > /dev/null 2>&1; /usr/sbin/hwclock --systohc)' >> /var/spool/cron/root
firewall-cmd --zone=public --add-port=10050/tcp --permanent
firewall-cmd --reload

