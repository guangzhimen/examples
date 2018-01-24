#!/usr/bin/env python
#coding:utf-8
from subprocess import Popen, PIPE
import MySQLdb
import sys
import re

reload(sys)
sys.setdefaultencoding("utf-8")


def ipmiconnt(server, user, passwd, database, ip):
    ipmidata = []
    dbserver = server
    dbuser = user
    dbpass = passwd
    dbbase = database
    db = MySQLdb.connect(dbserver, dbuser, dbpass, dbbase, charset='utf8')
    cursor = db.cursor()

    cursor.execute("select Customer003 from cmdb.cc_HostBase where InnerIP='%s'" % ip)
    ipmi_auth = cursor.fetchone()
    if ipmi_auth[0] == '':
        print "此ip所在服务器不存在IPMI控制器。"
    else:
        data_ch = [i for i in ipmi_auth[0].split()]
        ipmidata.append(data_ch[0])
        auth = [i for i in data_ch[1].split('/')]
        for i in range(len(auth)):
            ipmidata.append(auth[i])
        ipmidata.append(ipmidata[0].replace('/24', ''))
        del ipmidata[0]
        return ipmidata

def salt_ipmi_console(city, proxy, ip, user, passwd):
    db = MySQLdb.connect('192.168.1.1', 'mydb', '123456', 'cmdb', charset='utf8')
    cursor = db.cursor()
    cursor.execute("select DeviceClass from cmdb.cc_HostBase where InnerIP='%s'" % proxy)
    Device = cursor.fetchone()
    print Device
    city_dist = {"shandong": 'linux-10.10.129.19', "jiangsu": 'cmdb-proxy-154-9', "anhui": 'ah-cmdbproxy-31-59', "guangdong": 'gd-cmdbproxy-170-5', "guangxi-idc": 'gxid-cmdbproxy-136-12', "jilin": 'jl-cmdbproxy-188-17', "hainan": 'linux-10.131.193.80', "guangxi": 'linux-10.10.153.121', "guizhou": 'linux-10.10.155.88', "liaoning": 'linux-10.10.150.106', "hebei": 'linux-10.10.157.30', "neimeng": 'linux-10.10.156.114'}
    if city_dist.has_key(city) == True:
        if re.search('X8DTT|R6220|R5210P', Device[0]):
            p = Popen('salt %(proxy)s cmd.run "/srv/salt/exp %(ip)s ADMIN ADMIN super"' % {"proxy": city_dist[city], "ip": ip}, stdout = PIPE, stderr = PIPE, shell=True)
            stdout, stderr = p.communicate()
            print stdout
        elif re.search('PowerEdge', Device[0]):
            p = Popen('salt %(proxy)s cmd.run "/srv/salt/exp %(ip)s %(user)s %(passwd)s dell"' % {"proxy": city_dist[city], "ip": ip, "user": user, "passwd": passwd}, stdout = PIPE, stderr = PIPE, shell=True)
            stdout, stderr = p.communicate()
            print stdout

if __name__ == "__main__":
    data = ipmiconnt('192.168.3.55', 'api', 'axon@234', 'cmdb', sys.argv[2])
    print data
    salt_ipmi_console(sys.argv[1], sys.argv[2], data[2], data[0], data[1])
