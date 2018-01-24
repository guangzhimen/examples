#!/usr/bin/env python
#coding=utf-8
"""
cmdb数据采集客户端，实现数据数据采集上报之server端
通过socket完成，数据发送，读取同目录下conf文件，定义基础参数
数据格式均为json格式
ver：1.1.0
"""

from multiprocessing import cpu_count
from subprocess import Popen, PIPE
import platform
import socket
import time
import pdb
import argparse
import json
import sys
import logging
import psutil
import datetime

#初始化字符集编码
reload(sys)
sys.setdefaultencoding( "utf-8" )

#定义日志格式、文件信息
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%d %b %Y %H:%M:%S',
                    filename='error.log',
                    filemode='a+')

#pdb.set_trace()

#读取配置文件函数
def get_conf(key):
    conf_file = open('cmdbagent.conf', 'r')
    try:
        conf = json.load(conf_file)
    except ValueError:
        logging.error('Config file error')
    try:
        value = conf[key]
        return value
    except KeyError:
        return ''
    except UnboundLocalError:
        logging.error('Config file value format error')

#逻辑函数，判断是否使用命令行参数设置基础信息或者读取配置文件（优先读取配置文件）
def parameter(cmd):
    parameter_cmd = len(sys.argv)
    if parameter_cmd > 3:
	    arg = eval("args.%s" % cmd)
    else:
        arg = get_conf(cmd)
    return arg

#定义格式化命令行参数函数
def get_args():
    parser = argparse.ArgumentParser(description='Welcome AXON CMDB Agent' + '\n' + 'version: 1.0.2')
    parser.add_argument('-i', '--idcname', required=False, action='store', help="机房名称")
    parser.add_argument('-v', '--vpn', required=False, action='store', help="vpn地址")
    parser.add_argument('-a', '--agentip', required=False, action='store', help="内网ip")
    parser.add_argument('-b', '--bearerip', required=False, action='store', help="承载网地址")
    parser.add_argument('-V', '--Virtualip', required=False, action='store', help="虚拟地址VIP")
    parser.add_argument('-c', '--city', required=False, action='store', help="所在城市")
    parser.add_argument('print', help="打印主机信息")
    parser.add_argument('start', default='start', action='store_true', help="启动agent")

    args = parser.parse_args()
    return args


args = get_args() #函数变量

#获取系统版本函数
def sys_ver():
    version = open('/etc/redhat-release', 'r')
    ver = str(version.readline().split('\n')[0])
    version.close()
    return ver

#获取系统ip函数
def get_ip():
    p = Popen("ip add |grep inet |grep -v inet6 |awk '{print $2}' |awk -F/ '{print $1}'", stdout = PIPE, stderr = PIPE, shell=True)
    stdout, stderr = p.communicate()
    ipaddr = stdout.splitlines()
    ipaddr.remove('127.0.0.1')
    if '192.168.122.1' in ipaddr:
        ipaddr.remove('192.168.122.1')
    return ipaddr

#获取硬件信息函数
def getDMI():
    p = Popen('dmidecode', stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    return stdout

#处理硬件信息数据函数
def parserDMI(dmidata):
    pd = {}
    line_in = False
    for line in dmidata.split('\n'):
        if line.startswith('System Information'):
             line_in = True
             continue
        if line.startswith('\t') and line_in:
                 k,v = [i.strip() for i in line.split(':')]
                 pd[k] = v
        else:
            line_in = False
    return pd

#获取内存信息函数
def getMemTotal():
    cmd = "grep MemTotal /proc/meminfo"
    p = Popen(cmd, stdout = PIPE, shell = True)
    data = p.communicate()[0]
    mem_total = data.split()[1]
    memtotal = int(round(int(mem_total)/1024.0/1024.0, 0))
    return memtotal

#获取cpu信息函数
def getPyh():
    cmd = "cat /proc/cpuinfo"
    p = Popen(cmd, stdout = PIPE, stderr = PIPE, shell = True)
    stdout, stderr = p.communicate()
    return stdout

#获取cpu线程数
def getCpu():
     cpu_core = cpu_count()
     return cpu_core

#处理cpu信息数据
def parserPyh(stdout):
    groups = [i for i in stdout.split('\n\n')]
    group = groups[-2]
    cpu_list = [ i for i in group.split('\n')]
    cpu_info = {}
    for x in cpu_list:
        k, v = [i.strip() for i in x.split(':')]
        cpu_info[k] = v
    return cpu_info

#获取磁盘信息
def getDiskInfo():
    p = Popen("fdisk -l |awk '{print $2,$3}' |grep -e /dev/xv -e /dev/sd |sed 's/\,//g' |sed 's/\：/ /g'", stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    disk = stdout.splitlines()
    return disk

#对磁盘个数统计
def getDisknum():
    num = len(getDiskInfo())
    return num

#对磁盘容量求和
def getDisksum():
    disksum = []
    p = Popen("fdisk -l |awk '{print $2,$3}' |grep -e /dev/sd -e /dev/xv |sed 's/\：/ /g' |awk '{print $2}'", stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    disk = stdout.splitlines()
    for i in disk:
        disksum.append(float(i))
    disk_val = str(round(sum(disksum))) + 'G'
    return disk_val

#计算cpu使用率
def cpu_rate():
    cpu = psutil.cpu_times()
    sum = 0
    for i in range(len(cpu)):
        sum = sum + float(cpu[i])
    pcpu = 100 * (sum - float(cpu[3])) / sum
    cpu_r = str(round(pcpu)) + '%'
    return cpu_r

#计算内存使用率
def mem_rate():
    mem = psutil.virtual_memory()
    rate = round(float(mem[0] - mem[1]) / float(mem[0]) * 100)
    mem_r = str(rate) + '%' + ' ' + str(round((float(mem[0]) - float(mem[1])) / 1024**3, 2)) + 'G'
    return mem_r

#计算硬盘使用率
def disk_rate():
    dev = psutil.disk_partitions()
    list_dev = []
    for i in range(len(dev)):
        list_dev.append(dev[i].mountpoint)
    list_total = []
    list_used = []
    for x in range(len(list_dev)):
        list_total.append(psutil.disk_usage(list_dev[x])[0])
        list_used.append(psutil.disk_usage(list_dev[x])[1])
    rate = round(float(sum(list_used)) / float(sum(list_total)) * 100)
    disk_r = str(rate) + '%' + ' ' + str(sum(list_used) / 1024**3) + 'G'
    return disk_r

def start_time():
    stime = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    return stime

#主函数，格式化输出
def main():
    data_info = {}
    data_info['idcname'] = parameter('idcname')
    data_info['memory'] = getMemTotal()
    data_info['disk_num'] = getDisknum()
    data_info['disk'] = getDiskInfo()
    data_info['disk_sum'] = getDisksum()
    Pyhinfo = parserPyh(getPyh())
    data_info['cpu_num'] = getCpu()
    data_info['cpu_model'] = Pyhinfo['model name']
    data_info['ip'] = get_ip()
    data_info['city'] = parameter('city')
    data_info['inip'] = parameter('agentip')
    data_info['vpn'] = parameter('vpn')
    data_info['bip'] = parameter('bearerip')
    data_info['vip'] = parameter('Virtualip')
    try:
        data_info['SN'] = parserDMI(getDMI())['Serial Number']
        data_info['vendor'] = parserDMI(getDMI())['Manufacturer']
        data_info['Product'] = parserDMI(getDMI())['Product Name']
    except KeyError:
        data_info['SN'] = ''
        data_info['vendor'] = ''
        data_info['Product'] = '虚拟机'
        logging.error('data KeyError')
    data_info['hostname'] = platform.uname()[1]
    data_info['version'] = sys_ver()
    data_info['cpu_rate'] = cpu_rate()
    data_info['mem_rate'] = mem_rate()
    data_info['disk_rate'] = disk_rate()
    data_info['start_time'] = start_time()

    return data_info

result = main()

#定义客户端的socket
def post_socket():
    while True:
        result = main()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((get_conf('server'), int(get_conf('port'))))
            sock.sendall(json.dumps(result, ensure_ascii=False, encoding='utf-8'))
#            sock.recv(1024)
        except socket.error:
            logging.error('[Errno 111]' + ' ' + get_conf('server') + ':' + get_conf('port') + ' ' + 'Connection refused')
        sock.close()
        del result
        time.sleep(int(get_conf('time')))


if __name__ == "__main__":
    var = sys.argv[-1]
    if var == 'print':
        print json.dumps(result, ensure_ascii=False, encoding='utf-8')
    elif var == 'start':
        post_socket() 
