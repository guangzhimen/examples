#!/usr/bin/python
#coding:utf-8
import socket
import MySQLdb
import json
import pdb
import sys
import os
import logging
import argparse

reload(sys)
sys.setdefaultencoding("utf-8")

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%d %b %Y %H:%M:%S',
                    filename='error.log',
                    filemode='a+')

def get_args():
    parser = argparse.ArgumentParser(description='Welcome AXON CMDB Server' + '\n' + 'version: 1.0.2')
    parser.add_argument('start', help="启动服务端")
    parser.add_argument('stop', default='stop', action='store_true', help="关闭server端")

    args = parser.parse_args()
    return args

args = get_args()

def get_conf(key):
    conf_file = open('cmdbserver.conf', 'r')
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


def mysqlconnt(sdata, server, user, passwd, database):
    dbserver = server
    dbuser = user
    dbpass = passwd
    dbbase = database
    db = MySQLdb.connect(dbserver, dbuser, dbpass, dbbase, charset='utf8')
    cursor = db.cursor()

    num = cursor.execute("select HostID from cmdb.cc_HostBase where InnerIP='%s'" % sdata['inip'])

    if num == 0:
        cursor.execute('set @hostid = (select HostID from cmdb.cc_HostBase where HostID order by HostID desc limit 1)')

        cursor.execute('set @id =(select ID from cmdb.cc_ModuleHostConfig where ID order by ID desc limit 1)')

        cursor.execute("insert into cmdb.cc_HostBase \
                      (HostID,Cpu,CreateTime,DeviceClass,HostName,InnerIP,Mem,OSName,Region,Customer010,Source,Status,\
                       Customer001,Customer002,Customer004,Customer005,Customer008,\
                       Customer009) \
                       values (@hostid + 1,%(Cpu)s,now(),'%(DeviceClass)s','%(HostName)s','%(InnerIP)s','%(Mem)s',\
                       '%(OSName)s','%(Region)s','%(Customer010)s','1','在线','%(Customer001)s','%(Customer002)s',\
                       '%(Customer004)s','%(Customer005)s','%(Customer008)s','%(Customer009)s')" \
                       % {"Cpu": sdata['cpu_num'], "DeviceClass": sdata['Product'], "HostName": sdata['hostname'], \
                       "InnerIP": sdata['inip'], "Mem": sdata['memory'], "OSName": sdata['version'], \
                       "Region": sdata['city'], "Customer010": sdata['SN'], "Customer001": sdata['vip'], \
                       "Customer002": sdata['disk_sum'], "Customer004": sdata['bip'], "Customer005": \
                       sdata['vpn'], "Customer008": sdata['idcname'], "Customer009": sdata['disk_num']})

        cursor.execute("set @newid = (select HostID from cmdb.cc_HostBase where InnerIP='%s')" % sdata['inip'])

        cursor.execute('insert into cmdb.cc_ModuleHostConfig (ID,ApplicationID,HostID,ModuleID,SetID) values (@id + 1,1,@newid,1,1)')

    elif num == 1:
        cursor.execute("update cmdb.cc_HostBase set DeviceClass='%(DeviceClass)s',Cpu=%(Cpu)s,\
                       Mem=%(Mem)s,OSName='%(OSName)s',Region='%(Region)s',Customer001='%(Customer001)s',\
                       Customer002='%(Customer002)s',Customer004='%(Customer004)s',Customer005='%(Customer005)s',\
                       Customer008='%(Customer008)s',Customer009='%(Customer009)s',Customer010='%(Customer010)s' \
                       where InnerIP='%(InnerIP)s'" % {"Cpu": sdata['cpu_num'], "DeviceClass": sdata['Product'], \
                       "InnerIP": sdata['inip'], "Mem": sdata['memory'], "OSName": sdata['version'], \
                       "Region": sdata['city'], "Customer010": sdata['SN'], \
                       "Customer001": sdata['vip'], "Customer002": sdata['disk_sum'], \
                       "Customer004": sdata['bip'], "Customer005": sdata['vpn'], \
                       "Customer008": sdata['idcname'], "Customer009": sdata['disk_num']})
    db.commit()
    db.close()

#pdb.set_trace()
def socketserver(bindip, bindport, connect):
    print "Server is starting"  
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    sock.bind((bindip, bindport))
    connection = connect
    sock.listen(connection)
    print "Server is listenting port %s, with max connection %s" % (bindport, connection)
    while True:                 
        connection,address = sock.accept()     
        agentdata = connection.recv(10240)
        data = json.loads(agentdata, encoding='utf-8')
        while True:
            if not data:
                break
            else:
                print data
                try:
                    mysqlconnt(data, get_conf('dbserver'), get_conf('dbuser'), get_conf('dbpasswd') ,'cmdb')
                except:
                    logging.error(data['inip'] + ' ' + 'Failed to write data to the database')
            break
    connection.close() 

if __name__ == "__main__":
    var = sys.argv[1]
    if var == 'start':
        socketserver(get_conf('bindip'), int(get_conf('bindport')), int(get_conf('connect')))
    elif var == 'stop':
        os.system("ps -ef |grep server.py |grep -v grep |awk '{print $2}' |xargs kill -9")
