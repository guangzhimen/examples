#!/bin/bash
path=`pwd`
for ip in `cat ${path}/server.csv |awk -F"," 'NR>1 {print $1}'`
do
    disk=`awk -F"," -v i="${ip}" '{if(i==$1)print $3}' ${path}/server.csv`
    disk_type=`awk -F"," -v i="${ip}" '{if(i==$1)print $5}' ${path}/server.csv`
    size=`awk -F"," -v i="${ip}" '{if(i==$1)print $4}' ${path}/server.csv`
    if [ ${disk_type} == "ssd" ]; then
    	ansible-playbook ${path}/bin/ssd.yml -e "host=${ip} disk=${disk}"
    else
        if [ ${disk_type} == "hdd" ]; then
		ansible ${ip} -m shell -a "echo -e 'n\np\n1\n\n\nt\n8e\nw\n' | fdisk /dev/${disk}"
		ansible ${ip} -m shell -a "pvcreate /dev/${disk}1"
		ansible ${ip} -m shell -a "vgextend axon /dev/${disk}1"
		ansible ${ip} -m shell -a "lvextend -L +${size} /dev/axon/apps"
		ansible ${ip} -m shell -a "resize2fs /dev/axon/apps"
        fi
     fi	
done
