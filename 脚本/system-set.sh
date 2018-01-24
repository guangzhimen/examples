#!/bin/bash
language=`cat ~/.bashrc |grep LANG=zh_CN.UTF-8 |wc -l`
if [ $language -eq 0 ]; then
	echo "export LANG=zh_CN.UTF-8" >> ~/.bashrc
	source ~/.bashrc
fi
###############循环显示菜单######################################
while :
do
clear
cat << EOF
######################################################

	`date +'%Y-%m-%d -- %T'`

	
	1.set server ip and hostname

	2.set server ntp,zabbix-agent and ssh

	3.install vsftp server
	
	4.install tomcat server

	5.install redis server

        6.Add hard disk capacity

	7.exit

#####################################################
EOF
echo ""
echo ""
ssh_set ()
{
    ssh_check=`cat /etc/ssh/ssh_config |grep "#   StrictHostKeyChecking ask" |wc -l`
    if [ ${ssh_check} -eq 1 ]; then 
        sed -i 's/^#   StrictHostKeyChecking ask/StrictHostKeyChecking no/g' /etc/ssh/ssh_config
        systemctl restart sshd.service
        sleep 2
    fi
}

read -p "Input your choose number: " input
case ${input} in
1)	
while :
do
 echo ""
 if read -p "Set server ip and hostname(yes/no): " sip
    then
        case ${sip} in
            yes|y)
#                break
######配置服务器ip##################################################
inter=`ip add |grep " UP" |awk -F": " '{print $2}'`
inter_sum=`ip add |grep " UP" |awk -F": " '{print $2}' |wc -l`

message() {
while :
do
	read -p "please enter the IP address: " ip
        ipcheck=`echo ${ip} | grep -c '^[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}$'`
	if [ $ip == "exit" ]; then
		break 2
	fi
        if [ $ipcheck -eq 1 ]
        then
                break
        fi
        echo ""
        echo "You have not input a valid IP Address!"
done
while :
do
	read -p "please enter the NETMASK address: " netmask
        maskcheck=`echo ${netmask} | grep -c '^[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}$'`
	if [ $netmask == "exit" ]; then
		break 2
	fi
        if [ $maskcheck -eq 1 ]
        then
                break
        fi
        echo ""
        echo "You have not input a valid NETMASK Address!"
done
while :
do
	read -p "please enter the GATEWAY address: " gateway
        gatewaycheck=`echo ${gateway} | grep -c '^[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}$'`
	if [ $gateway == "exit" ]; then
		break 2
	fi
        if [ $gatewaycheck -eq 1 ]
        then
                break
        fi
        echo ""
        echo "You have not input a valid GATEWAY Address!"
done
}
while :
do
 if read -p "Set your server hostname(yse/no): " host
    then
        case ${host} in
            yes|y)
		read -p "Please input hostname: " host
        	gatewaycheck=`echo ${host} | grep -c '^[a-z].*$'`
		if [ $host == "exit" ]; then
			break 2
		fi
        	if [ $gatewaycheck -eq 1 ]
        	then
                	echo ${host} > /etc/hostname
			if [ $? -eq 0 ]; then
                        	echo -e "\033[32m [ ok ]\033[0m"
                	else
                        	echo -e "\033[31m [ fales ] \033[0m"
                fi
                break
        	fi
        echo ""
        echo "You have not input a valid Hostname!"
#                break
            ;;
             no|n)
                break
            ;;
              *)
                echo "Input parameter error !"
                continue
    esac
fi
done

if [ ${inter_sum} -eq 1 ]; then
	message

cat << EOF > /etc/sysconfig/network-scripts/ifcfg-$inter
TYPE=Ethernet
BOOTPROTO=none
IPADDR=$ip
NETMASK=$netmask
GATEWAY=$gateway
NAME=$inter
DEVICE=$inter
ONBOOT=yes
DNS1=223.5.5.5
EOF

else
	message
	echo -e "\033[31m######   Network Message   #######\033[0m"
	ip addr
	read -p "please enter the INTERFACE address: " shi

cat << EOF > /etc/sysconfig/network-scripts/ifcfg-$shi
TYPE=Ethernet
BOOTPROTO=none
IPADDR=$ip
NETMASK=$netmask
GATEWAY=$gateway
NAME=$shi
DEVICE=$shi
ONBOOT=yes
DNS1=223.5.5.5
EOF
fi
sleep 1
/etc/init.d/network restart
sleep 5
sed -i 's/^#UseDNS/UseDNS no/g' /etc/ssh/sshd_config
ssh_set
for((i=1;i<=5;i++))
do
	pingcheck=`ping -c1 -w1 192.168.3.23 |wc -l`
        if [ $pingcheck -eq 6 ]; then
		sleep 1
		echo ""
                echo -e "Check network connection is \033[32m [ ok ]\033[0m"
		break
        else
		echo ""
                echo -e "Check network connection is \033[31m [ fales ] \033[0m"
        fi
done
            ;;
             no|n)
                break
            ;;
              *)
                echo "input parameter error !"
                continue
    esac
fi
done
;;
############配置ntp和zabbix_agent################
2)	
while :
do
 echo ""
 if read -p "Set your server ntp and zabbix_agent (yes/no): " ntp
    then
        case ${ntp} in
            yes|y)
	    zabbix () {
		sed -i '/^Server=/c Server=192.168.1.12' /apps/usr/zabbix/etc/zabbix_agentd.conf
		sed -i '/^ServerActive=/c ServerActive=192.168.1.12' /apps/usr/zabbix/etc/zabbix_agentd.conf
		sed -i 's/^#UseDNS/UseDNS no/g' /etc/ssh/sshd_config
		ssh_set
		wget http://192.168.3.23/conf/zabbix.service;mv zabbix.service /lib/systemd/system
		systemctl restart zabbix.service
		systemctl enable zabbix.service
		sed -i '/10.10.10.10/d' /var/spool/cron/root
		sed -i '/192.168.1.1/d' /var/spool/cron/root
		echo '0 1 * * * ( /usr/sbin/ntpdate 192.168.1.1  > /dev/null 2>&1; /usr/sbin/hwclock --systohc)' >> /var/spool/cron/root
		ntpdate 192.168.1.1 > /dev/null
		}
		zabbix
                if [ $? -eq 0 ]; then
                        echo -e "\033[32m [ ok ]\033[0m"
                else
                        echo -e "\033[31m [ fales ] \033[0m"
                fi
#                break
            ;;
             no|n)
                break
            ;;
              *)
                echo "Input parameter error !"
                continue
    esac
fi
done 
;;
###############安装vsftp服务#######################
3)
while :
do
 echo ""
 if read -p "Install vsftp (yes/no): " ftp
    then
        case ${ftp} in
            yes|y)
	    vsftp() {
		systemctl stop firewalld.service
        	ssh_set
		wget http://192.168.3.23/soft/vsftpd-el7-axon.tar.gz;mv vsftpd-el7-axon.tar.gz /apps/usr
		wget http://192.168.3.23/conf/ftpuseradd.sh
		chmod -R 755 /root/ftpuseradd.sh
		tar -zxvf /apps/usr/vsftpd-el7-axon.tar.gz -C /apps/usr > /dev/null
		/apps/usr/vsftpd/install.sh > /dev/null
		}
		vsftp
		if [ $? -eq 0 ]; then
			echo -e "\033[32m [ ok ]\033[0m"
		else
			echo -e "\033[31m [ fales ] \033[0m"
		fi
#                break
            ;;
             no|n)
                break
            ;;
              *)
                echo "Input parameter error !"
                continue
    esac
fi
done
;;
###############安装tomcat服务#######################
4)
while :
do
 echo ""
 if read -p "Install tomcat (yes/no): " tomcat
    then
        case ${tomcat} in
            yes|y)
	    tomcat() {
                ssh_set
		wget http://192.168.3.23/soft/java-1.8.0_91.tar.gz;mv java-1.8.0_91.tar.gz /apps/usr
		wget http://192.168.3.23/soft/tomcat-axon.tar.gz;mv tomcat-axon.tar.gz /apps/usr
                tar -zxvf /apps/usr/java-1.8.0_91.tar.gz -C /apps/usr > /dev/null
		        tar -zxvf /apps/usr/tomcat-axon.tar.gz -C /apps/usr > /dev/null
cat << EOB >> /etc/profile
JAVA_HOME=/apps/usr/java/jdk1.8.0_91
PATH=/apps/usr/java/jdk1.8.0_91/bin:/bin:$PATH
JRE_HOME=/apps/usr/java/jdk1.8.0_91/jre
CLASSPATH=.:/apps/usr/java/jdk1.8.0_91/lib:/apps/usr/java/jdk1.8.0_91
export JAVA_HOME
export PATH
export JRE_HOME
export CLASSPATH
EOB
		        source /etc/profile
                firewall-cmd --zone=public --add-port=8080/tcp --permanent
                firewall-cmd --reload
		        /apps/usr/tomcat-axon/bin/startup.sh
		        chmod 755 /etc/rc.d/rc.local
		        echo /apps/usr/tomcat-axon/bin/startup.sh >> /etc/rc.d/rc.local
		}
		tomcat
                if [ $? -eq 0 ]; then
                        echo -e "\033[32m [ ok ]\033[0m"
                else
                        echo -e "\033[31m [ fales ] \033[0m"
                fi
#                break
            ;;
             no|n)
                break
            ;;
              *)
                echo "Input parameter error !"
                continue
    esac
fi
done
;;
###############安装redis服务#######################
5)
while :
do
 echo ""
 if read -p "Install redis (yes/no): " redis
    then
        case ${redis} in
            yes|y)
	    redisinstall() {
		systemctl stop firewalld.service
        	ssh_set
		echo 1 >> /proc/sys/vm/overcommit_memory
                firewall-cmd --zone=public --add-port=6379/tcp --permanent
                firewall-cmd --reload
		wget http://192.168.3.23/soft/redis-3.2-axon.tar.gz;mv redis-3.2-axon.tar.gz /apps/usr
		tar -zxvf /apps/usr/redis-3.2-axon.tar.gz -C /apps/usr > /dev/null
		wget http://192.168.3.23/conf/redis.conf;mv redis.conf /apps/usr/redis
		/apps/usr/redis/bin/redis-server /apps/usr/redis/redis.conf
		}
		redisinstall
		if [ $? -eq 0 ]; then
			echo -e "\033[32m [ ok ]\033[0m"
		else
			echo -e "\033[31m [ fales ] \033[0m"
		fi
#                break
            ;;
             no|n)
                break
            ;;
              *)
                echo "Input parameter error !"
                continue
    esac
fi
done
;;
###############扩容磁盘容量#######################
6)
while :
do
 echo ""
 echo "display all hard disk"
 echo ""
 fdisk -l |grep /dev/sd\[a-z\]：|sed 's/\：/ /g' |awk '{print $2,$3}'
 echo ""
 if read -p "Are you sure you need to expand your hard drive? (yes/no): " disk
    then
        case ${disk} in
            yes|y)
                while :
                do
                echo ""
                if read -p "Is it ssd? (yes/no): " ssd
                then
                    case ${ssd} in
                    yes|y)
                	while :
                	do
                        	if read -p "please input SSD disk dev name ( [example: sdb] [directory: /ssd] ): " ssdn
				then
				case ${ssdn} in
				exit)
					break 3
				;;
				sd[a-z])
					ssdout=`fdisk -l |grep /dev/sd\[a-z\]： |grep ${ssdn} |wc -l`
					if [ ${ssdout} -eq 0 ]; then
						echo ""
						echo "SSD Disk is not found! Please input again."
						break
					else
						while :
						do
						if read -p "Make sure you want to add a disk partition (yes/no): " ssdcommit
						then
						case ${ssdcommit} in
						yes|y)
							mkdir -p /ssd
                        				echo -e 'n\np\n1\n\n\nw\n' | fdisk /dev/${ssdn}
                        				mkfs -t ext4 /dev/${ssdn}1
                        				uuid=`blkid |grep \/dev\/${ssdn}1 |awk '{print $2}'` && echo "$uuid  /ssd  ext4  defaults  0 0" >> /etc/fstab
                        				sed -i 's/\"//g' /etc/fstab
                        				mount -a
                        				if [ $? -eq 0 ]; then
                            					echo -e "\033[32m [ ok ]\033[0m"
                            					sleep 1
                        				else
                            					echo -e "\033[31m [ fales ] \033[0m"
                        				fi
						;;
						no|n)
							break 2
						;;
						*)
							echo "input error!"
						esac
						fi
						done
					fi
					;;
				*)
                        		echo ""
                        		echo "You inputed SSD name is wrong!"
				esac
				fi
                        done
                        ;;
                        no|n)
                            break
                        ;;
                        *)
                            echo "Input parameter error !"
                            continue
                        esac
                        fi
                        done
		while :
		do
                	if read -p "please input LVM hard disk dev name ( [example: sdb] [disdirectory: /apps] ): " hhd
                        then 
                    case ${hhd} in
                        exit)
                            break 2
                            ;;
                        sd[a-z])
                            hhdout=`fdisk -l |grep /dev/sd\[a-z\]： |grep ${hhd} |wc -l`
                    	    if [ ${hhdout} -eq 0 ]; then
				echo ""
                        	echo "Hard disk is not found! Please input again."
                    	    else
                        	break
                    	    fi
                    	    ;;
                    	     *)
        			echo ""
        			echo "You inputed hard drive name is wrong!"
            	    esac
		    fi
		done
		while :
		do
                	if read -p "please input disk size (example:500): " size
			then
			case $size in
				exit)
					break 2
				;;
				[0-9][0-9][0-9]|[0-9][0-9][0-9][0-9])
					sizeout=`fdisk -l |grep ${hhd}：|sed 's/\：/ /g'|awk -v val=$size '{if($3>val)print $3}' |wc -l`
                        		if [ $sizeout -eq 0 ]; then
						echo ""
                                		echo "The input size exceeds the hard disk size! Please input again."
					else
						break
                                        break
                                fi
				;;
				*)
                        		echo ""
                        		echo "You inputed hard drive size is wrong!"
				esac
			fi
                        done
		while :
		do
		if read -p "Make sure you want to add a LVM disk partition (yes/no): " hhdcommit
		then
		case ${hhdcommit} in
		yes|y)
                	echo -e 'n\np\n1\n\n\nt\n8e\nw\n' | fdisk /dev/${hhd}
                	pvcreate /dev/${hhd}1
                	vgextend axon /dev/${hhd}1
                	lvextend -L +${size}G /dev/axon/apps
                	resize2fs /dev/axon/apps
                	if [ $? -eq 0 ]; then
                        	echo -e "\033[32m [ ok ]\033[0m"
				break 2
                	else
                        	echo -e "\033[31m [ fales ] \033[0m"
                	fi
			;;
		no|n)
			break
		;;
		*)
			echo "input error!"
		esac
		fi
		done
#                break
            ;;
             no|n)
                break
            ;;
              *)
                echo "Input parameter error !"
                continue
    esac
fi
done
;;
###################退出############################
7)
	exit
esac
done
exit 0
