#!/bin/bash
info() {
ansible jiangsu-idc -m shell -a "/etc/ansible/script/df.sh" >/dev/null
ansible jiangsu-idc -m fetch -a "src=/root/info.txt dest=/root/ flat=yes" >/dev/null
ansible jiangsu-idc -m shell -a "rm -rf /root/info.txt" >/dev/null
}
info
disk_volume=`cat /root/info.txt | sed 's/\%/ /g'| awk -F, '{if($2>=85){print $2}}' | wc -l`
es_stat=`cat /root/info.txt |tail -1`
mail_user=yunwei@xxxxx
        if [ $es_stat == "red" ]; then
                echo "elasticsearch stat is RED ERROR!" | mail -s "elasticsearch集群状态红色告警，请处理！" $mail_user
                echo "`date +'%Y%m%d-%T'` elasticsearch stat is RED ERROR!" >> /root/es_disk.log
        elif [ $es_stat == "yellow" ]; then
                echo "elasticsearch stat is YELLOW WARNING!" | mail -s "elasticsearch集群状态黄色告警，请处理！" $mail_user
                echo "`date +'%Y%m%d-%T'` elasticsearch stat is YELLOW WARNING!" >> /root/es_disk.log
        fi
	if [ ${disk_volume} -gt 1 ]; then
		echo "disk vol /apps volume is > 85%" | mail -s "elasticsearch集群数据盘使用率大于85%，请处理！" $mail_user
		echo "`date +'%Y%m%d-%T'` elasticsearch disk vol /apps volume is > 85%" >> /root/es_disk.log
		cat /root/info.txt >> /root/es_disk.log
		ansible jiangsu-idc -m shell -a "/etc/ansible/script/delete_es_index.sh" >/dev/null
		info
		disk_volume=`cat /root/info.txt | sed 's/\%/ /g'| awk -F, '{if($2>85){print $2}}' | wc -l`
		rm -rf /root/info.txt
		if [ $disk_volume -le 1 ]; then
			echo "disk vol /apps volume is recover" | mail -s "elasticsearch集群数据盘使用率已恢复到正常值！" $mail_use
			echo "`date +'%Y%m%d-%T'` elasticsearch disk vol /apps volume is recover" >> /root/es_disk.log
			cat /root/info.txt >> /root/es_disk.log
		fi	
	fi
if [ ${disk_volume} -le 1 ]; then
	echo "`date +%Y%m%d-%T` program is running done!" >> /root/es_disk.log
	cat /root/info.txt >> /root/es_disk.log
fi
rm -rf /root/info.txt
