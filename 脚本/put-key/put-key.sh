#!/bin/bash
path=`pwd`

for ip in `cat /root/ras/ip.txt`
do
echo 'echo BEGIN!; mkdir -p /root/.ssh' | setsid env SSH_ASKPASS="${path}/passwd.sh" DISPLAY="none:0" ssh root@${ip} 2>&1
setsid env SSH_ASKPASS="${path}/passwd.sh" DISPLAY="none:0" scp ~/.ssh/authorized_keys ${ip}:/root/.ssh 2>&1
done
