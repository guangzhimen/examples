#!/bin/bash
#
path=`pwd`
for ip in `cat ${path}/server.csv |awk -F"," 'NR>1 {print $1}'`
do
passfile=`touch ${path}/put-key/password/${ip}.sh`
passdvar=`awk -F"," -v i="${ip}" '{if(i==$1)print $8}' ${path}/server.csv`
host_ip=`cat /etc/ansible/hosts |grep ${ip} |wc -l`
cat << EOF > ${path}/put-key/password/${ip}.sh
#!/bin/bash
echo '${passdvar}'
EOF
chmod -R 755 ${path}/put-key/password/${ip}.sh
echo "echo [ putting.... ${ip} ]; mkdir -p /root/.ssh" | setsid env SSH_ASKPASS="${path}/put-key/password/${ip}.sh" DISPLAY="none:0" ssh root@${ip} 2>&1
setsid env SSH_ASKPASS="${path}/put-key/password/${ip}.sh" DISPLAY="none:0" scp `pwd`/put-key/file/auth.sh root@${ip}:/root/.ssh 2>&1
echo "sh /root/.ssh/auth.sh" | setsid env SSH_ASKPASS="${path}/put-key/password/${ip}.sh" DISPLAY="none:0" ssh root@${ip} 2>&1
echo "rm -rf /root/.ssh/auth.sh" | setsid env SSH_ASKPASS="${path}/put-key/password/${ip}.sh" DISPLAY="none:0" ssh root@${ip} 2>&1

if [ $? -eq 0 ]; then
	if [ ${host_ip} -eq 0 ]; then
        	echo "${ip}" >> /etc/ansible/hosts
	fi
	echo -e "\033[32m [ ok ]\033[0m"
else
	echo -e "\033[31m [ fales ] \033[0m"
fi
done
