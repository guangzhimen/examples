#!/bin/bash
path=`pwd`
for ip in `cat ${path}/server.csv |awk -F"," 'NR>1 {print $1}'`
do
    host=`awk -F"," -v i="${ip}" '{if(i==$1)print $2}' ${path}/server.csv`
    ansible ${ip} -m shell -a "echo ${host} > /etc/hostname"
done
