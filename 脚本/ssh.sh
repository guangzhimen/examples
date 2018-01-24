#!/bin/bash

source /etc/profile

case "$1" in
	zhejiang)
	   ssh 124.160.193.94 -p443
	   ;;
	hainan)
	   ssh 60.13.122.28 -p443
	   ;;
	hubei)
	   ssh 113.57.230.2 -p443
	   ;;
      neimeng)
           ssh 60.31.214.40 -p20314
           ;;
      anhui)
           ssh 112.122.11.167 -p22213
           ;;
      sichuan)
           ssh 119.4.250.73
           ;;
       guangdong)
           ssh 220.199.6.57 -p21
           ;;
      guangxi)
           ssh 121.31.253.125 -p443
           ;;
      guangxi-idc)
           ssh 221.7.213.133 -p22216
           ;;
       hunan)
           ssh 110.52.11.183 -p12071
           ;;
      guizhou)
           ssh 221.13.34.41 -p22239
           ;;
      hebei)
           ssh 221.192.132.36 -p22028
           ;;
       shandong)
           ssh 112.231.23.157 -p3589
           ;;
      jilin)
           ssh 122.141.253.28
           ;;
      liaoning)
           ssh 218.60.136.94 -p12070
	   ;;
      niaoling-yi)
	   ssh 218.61.60.213 -p22213
           ;;  
      jiangsu)
           ssh 122.194.5.183 -p8443
           ;;
      jiangsu-idc)
           ssh 122.192.33.36 -p21214
           ;;
	*)
	   echo "Usage: {zhejiang|hubei|neimeng|anhui|sichuan|guangdong|guangxi|guangxi-idc|hunan|guizhou|hebei|shandong|jilin|liaoning|jiangsu|jiangsu-idc}"
esac
exit 0
