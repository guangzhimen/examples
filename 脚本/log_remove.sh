#!/bin/bash
function action_m() {
for i in `ls -lht |awk '{print $5,$9}' |grep M |awk '{print $2}'`
do
    sed -i '/[0-9]\{2\}\/[A-Za-z]\{3\}\/2017/d' $i &
done

while :
do
    if [ `ps -ef |grep 'sed -i' |grep -v grep |wc -l` -eq 0 ]; then
        /apps/usr/nginx/sbin/nginx -t
        /apps/usr/nginx/sbin/nginx -s reload
        break
    fi
done
}

function action_g() {
for i in `ls -lht |awk '{print $5,$9}' |grep G |awk '{print $2}'`
do
    sed -i '/[0-9]\{2\}\/[A-Za-z]\{3\}\/2017/d' $i &
done

while :
do
    if [ `ps -ef |grep 'sed -i' |grep -v grep |wc -l` -eq 0 ]; then
        /apps/usr/nginx/sbin/nginx -t
        /apps/usr/nginx/sbin/nginx -s reload
        break
    fi
done
}

if [ `ls -lht |awk '{print $5,$9}' |grep M |awk '{print $2}' |wc -l` -ne 0 ]; then
    action_m
fi
if [ `ls -lht |awk '{print $5,$9}' |grep G |awk '{print $2}' |wc -l` -ne 0 ]; then
    action_g
fi
