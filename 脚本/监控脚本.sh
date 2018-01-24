#!/bin/bash
########变量函数##########
function fun() {
	mail_user=liyj@axon.com.cn
	timeout=10
	curl_url_ok=`timeout 3 curl -I -k -u admin:axon@234 https://122.192.33.44 |grep HTTP |awk '{print $2}'`
	curl_url_timeout=`timeout ${timeout} curl -I -k -u admin:axon@234 https://122.192.33.44 |grep HTTP |wc -l`
      }

#######定义打印日志格式函数#############
function errors() {
	   if [ ${curl_url_ok} != "200" ]; then
		echo `date +'%Y%m%d-%T'` 'elk web is error' >> /root/monitor-`date +'%y%m%d'`.log
	   fi
	   if [ ${curl_url_timeout} -eq 0 ]; then
		echo `date +'%Y%m%d-%T'` 'elk web is timeout > 10s' >> /root/monitor-`date +'%y%m%d'`.log
	   fi
}

########定义监测恢复状态函数############
function check() {
           if [ ${curl_url_ok} -eq 200 ] && [ ${curl_url_timeout} -eq 1 ]; then
           	echo "https://122.192.33.44 ELKstak web recover" | mail -s "ELK系统页面已恢复" ${mail_user}
           	echo `date +'%Y%m%d-%T'` 'elk web [recover]' >> /root/monitor-`date +'%y%m%d'`.log
                break
           fi
        }

###########定义监测控制流程##############
while :
do
fun
	sleep 1
	if [ ${curl_url_ok} -eq 200 ] && [ ${curl_url_timeout} -eq 1 ]; then
		echo "recover" >/dev/null
		
	else
		while :
		do
			sleep 1
				if [ ${curl_url_ok} -ne 200 ] || [ ${curl_url_timeout} -eq 0 ]; then
					echo "https://122.192.33.44 ELKstak web is down" | mail -s "ELK系统页面无法访问" ${mail_user}
					errors
					while :
					do
					fun
						sleep 1
						if [ ${curl_url_ok} = "200" ] && [ ${curl_url_timeout} -eq 1 ]; then
							check
							break
						else
							errors
						fi
					done
				else
					break
				fi
		done	
	fi	
done	
	
