#!/bin/bash
#创建vsftp用户
user_path="/apps/usr/ftpuser"
read -p "用户名:" usr
read -p "密码:" passd
read -p "目录:" directory
arealy=$(cat /etc/passwd |grep ${usr} |wc -l)
group=$(cat /etc/group |grep ${usr} |wc -l)
        if [ $arealy -eq 0 ] || [ $group -eq 0 ];then
	     if [ -d "$directory" ];then
                cut=`echo ${directory} |awk -F"/" '{print $NF}'`
                path=`echo ${directory} |sed "s/${cut}//g"`
                id=$(ls -lht ${path} |grep ${cut} |awk '{print $4}')
		/usr/sbin/useradd -d ${directory} -s /sbin/nologin ${usr}
			if [ $id == "root" ] || [ $id == "service" ]; then
				chown -R $usr.$usr $directory
				mkdir -p /apps/usr/ftpuser
				chmod 755 /apps/usr/ftpuser
                		echo $passd |passwd --stdin $usr >/dev/null
                		echo -e "\nuser: ${usr}  password: ${passd}  directory:${directory}" >> $user_path/user.txt
			else
				mkdir -p /apps/usr/ftpuser
                		chmod 755 /apps/usr/ftpuser
                		usermod -G $id $usr
                		echo $passd |passwd --stdin $usr >/dev/null
                		echo -e "\nuser: ${usr}  password: ${passd}  directory:${directory}" >> $user_path/user.txt
			fi
	    else
		mkdir -p $directory
                mkdir -p /apps/usr/ftpuser
                chmod 755 /apps/usr/ftpuser
                /usr/sbin/useradd -d ${directory} -s /sbin/nologin ${usr}
                chmod 755 ${directory}
                echo $passd |passwd --stdin $usr >/dev/null
		chown -R $usr.$usr $directory
                echo -e "\nuser: ${usr}  password: ${passd}  directory:${directory}" >> $user_path/user.txt
	    fi
        else
                echo "此用户已存在"
                exit 1
        fi
