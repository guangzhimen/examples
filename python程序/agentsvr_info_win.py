#coding=utf-8
"""
cmdb数据采集客户端，实现数据数据采集上报之server端
通过socket完成，数据发送，读取同目录下conf文件，定义基础参数
数据格式均为json格式
ver：1.0.1
"""

from multiprocessing import cpu_count
from subprocess import Popen, PIPE
import platform
import wmi
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

c = wmi.WMI()

#定义日志格式、文件信息
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%d %b %Y %H:%M:%S',
                    filename='error.log',
                    filemode='a+')

#pdb.set_trace()

#读取配置文件函数
#读取配置文件函数
def get_conf(key):
    conf_file = open('cmdbagent.conf', 'r')
    conf_r = conf_file.read()
    try:
        conf = eval(conf_r)
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
    parser = argparse.ArgumentParser(description='Welcome AXON CMDB Agent' + '\n' + 'version: 1.1.0')
    parser.add_argument('-i', '--idcname', required=False, action='store', help="机房名称".decode('utf-8').encode('gbk'))
    parser.add_argument('-v', '--vpn', required=False, action='store', help="VPN地址".decode('utf-8').encode('gbk'))
    parser.add_argument('-a', '--agentip', required=False, action='store', help="本地IP地址".decode('utf-8').encode('gbk'))
    parser.add_argument('-b', '--bearerip', required=False, action='store', help="承载网地址".decode('utf-8').encode('gbk'))
    parser.add_argument('-V', '--Virtualip', required=False, action='store', help="VIP地址".decode('utf-8').encode('gbk'))
    parser.add_argument('-c', '--city', required=False, action='store', help="城市".decode('utf-8').encode('gbk'))
    parser.add_argument('print', help="打印主机信息".decode('utf-8').encode('gbk'))
    parser.add_argument('start', default='start', action='store_true', help="启动agent".decode('utf-8').encode('gbk'))

    args = parser.parse_args()
    return args


args = get_args() #函数变量

#获取系统版本函数
def sys_ver():
    system = platform.system()
    version = platform.release()
    core = platform.architecture()[0]
    ver = system + ' ' + version + ' ' + core
    return ver

#获取系统ip函数
def get_ip():
    ipaddr = ''
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        ipaddr = ip
    return ipaddr

#获取硬件信息函数
def getDMI(pyh):
    p = Popen(pyh, stdout=PIPE, stderr=PIPE, shell=True)
    stdout = list(p.communicate())
    del stdout[1]
    pyhdata = stdout[0]
    DMI = pyhdata.splitlines()[2]
    return DMI


#获取内存信息函数
def getMemTotal():
    mem = []
    for memModule in c.Win32_PhysicalMemory():
        mem.append(long(memModule.Capacity) / (1024**3))
    return str(sum(mem))


#获取cpu线程数
def getCpu():
     cpu_core = cpu_count()
     return cpu_core


#对磁盘个数统计
def getDisknum():
    disklist = [] 
    for physical_disk in c.Win32_DiskDrive (): 
        diskdict = {} 
        diskdict["Caption"] = physical_disk.Caption  
        disklist.append(diskdict)
    return len(disklist)

#对磁盘容量求和
def getDisksum():
    sumdisk = []
    for disk in c.Win32_LogicalDisk (DriveType=3):
        sumdisk.append(float(long(disk.Size) / ( 1024**3 )))
    disk_val = str(round(sum(sumdisk))) + 'G'

    return disk_val

#计算cpu使用率
def cpu_rate():
    cpu = psutil.cpu_times()
    cpu_val = []
    for i in range(len(cpu)):
        cpu_val.append(float(cpu[i]))
    sum_total = float(sum(cpu_val))
    pcpu = 100 * (sum_total - float(cpu[2])) / sum_total
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
    list_other = []
    for i in range(len(dev)):
        if dev[i].opts == 'rw,fixed':
            list_dev.append(dev[i].mountpoint)
        else:
            list_other.append(dev[i].mountpoint)
    list_total = []
    list_used = []
    for x in range(len(list_dev)):
        list_total.append(psutil.disk_usage(list_dev[x])[0])
        list_used.append(psutil.disk_usage(list_dev[x])[1])
    rate = round(float(sum(list_used)) / float(sum(list_total)) * 100)
    disk_r = str(rate) + '%' + ' ' + str(sum(list_used) / 1024**3) + 'G'
    return disk_r

#系统启动时间
def start_time():
    stime = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    return stime


#主函数，格式化输出
def main():
    data_info = {}
    data_info['idcname'] = parameter('idcname')
    data_info['memory'] = getMemTotal()
    data_info['disk_num'] = getDisknum()
    data_info['disk_sum'] = getDisksum()
    data_info['cpu_num'] = getCpu()
    data_info['ip'] = get_ip()
    data_info['city'] = parameter('city')
    data_info['inip'] = parameter('agentip')
    data_info['vpn'] = parameter('vpn')
    data_info['bip'] = parameter('bearerip')
    data_info['vip'] = parameter('Virtualip')
    data_info['SN'] = getDMI('wmic bios get serialnumber')
    data_info['Product'] = getDMI('wmic CSPRODUCT get name')
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
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((get_conf('server'), int(get_conf('port'))))
            sock.sendall(json.dumps(result, ensure_ascii=False).decode('gbk').encode('utf-8'))
        except socket.error:
            logging.error('[Errno 111]' + ' ' + get_conf('server') + ':' + get_conf('port') + ' ' + 'Connection refused')
        sock.close()
        time.sleep(int(get_conf('time')))


if __name__ == "__main__":
    var = sys.argv[-1]
    if var == 'print':
        print json.dumps(result, ensure_ascii=False)
    elif var == 'start':
        post_socket()
