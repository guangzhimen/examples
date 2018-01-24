#!/bin/bash
#
clear
trap "" SIGINT
while :
do
clear
echo "                          *******************************************************************"
echo "                          **                                                               **"
echo "                          **                     批量系统配置程序                          **"
echo "                          **                    system info manage                         **"
echo "                          **          	      `date +'%Y-%m-%d -- %T'`                       **"
echo "                          **                    AXON yunwei system                         **"
echo "                          **		  					           **"
echo "                          *******************************************************************"
cat << EOF

                                     ********please enter your choise********
	
		                  (1) 批量分发ssh密钥功能（用户ansible认证使用）

				  (2) 检查服务器ansible连通性

		                  (3) 批量配置服务器hostname

		                  (4) 批量更改zabbix-agent配置文件并重启进程、配置更新ntp

		                  (5) !!警告!! (操作磁盘有风险，请慎重) 批量扩容数据目录/apps(要求此目录分区必须为LVM)
		                      批量挂载ssd盘到/ssd目录，系统会自动识别扩容或者挂在 

		                  (6) 上传表格文件（server.csv）为上述配置做准备

		                  (7) 下载表格文件模板 (server.csv)

		                  (8) 扫描网段内空闲ip 

				  (9) 查看服务器系统信息【开发中...】

		                  (10) 退出
EOF
echo ""
echo ""

read -p "请输入选项序号: " input
path=`pwd`
case ${input} in
1)	
while :
do
 echo ""
 if read -p "Put ssh key in servers (yes/no): " key
    then
        case ${key} in
            yes|y)
               `pwd`/put-key/put-key.sh
#                break
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

2)
while :
do
 echo ""
 if read -p "test server connected (yes/no): " con
    then
        case ${con} in
            yes|y)
               ansible all -m ping
#                break
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

8)
while :
do
 echo ""
 if read -p "check network [192.168.1.0] (yes/no): " check
    then
        case ${check} in
            yes|y)
             python `pwd`/bin/ip_check.py
	     while :
		do
 		if read -p "Get ip ping down list ? (yes/no): " list
    		then
        		case ${list} in
            			yes|y)
             			sz /apps/home/ansible/log/ip_down.log
		                break
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
#                break
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

4)
while :
do
 echo ""
 if read -p "system initialization (yes/no): " init
    then
        case ${init} in
            yes|y)
               `pwd`/bin/init.sh
#                break
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

3)
while :
do
 echo ""
 if read -p "set hostname (yes/no): " host
    then
        case ${host} in
            yes|y)
               `pwd`/bin/batch-hostname.sh
#                break
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
5)
while :
do
    echo ""
    if read -p "!!!!![WRONGING]!!!!! set disk (yes/no): " disk
        then
            case ${disk} in
                yes|y)
                    `pwd`/bin/disk.sh
 #                   break
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
6)
while :
do
    echo ""
    if read -p "put your server.csv file (yes/no): " put
        then
            case ${put} in
                yes|y)
		    rm -rf ~/server.csv
		    sleep
		    rz
                    break
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
7)
while :
do
    echo ""
    if read -p "Get server.csv file (yes/no): " get
        then
            case ${get} in
                yes|y)
                    sz ${path}/template/server.csv
                    break
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
10)
	exit
;;
esac
done
