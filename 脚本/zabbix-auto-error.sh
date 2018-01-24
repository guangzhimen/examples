#!/bin/bash
#######zabbix auto error handle #########
value=$(mysql -u xxxx -pxxxx -h 10.10.188.210 -Ne "select * from zabbix.alerts order by alertid desc limit 100;" |grep "test-141.38 is unreachable for 5 minutes" |wc -l)
   
   if [ $value -ge 1 ];then      
   /usr/bin/ansible-playbook /etc/ansible/playbooks/test.yml > /dev/null 2>1&
   mysql -u xxxx -pxxxx -h 10.10.188.210 -Ne "delete from zabbix.alerts where message like '%test-141.38 is unreachable for 5 minutes%';"
fi
