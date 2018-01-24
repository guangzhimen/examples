#!/usr/bin/env python
#coding:utf-8
import MySQLdb
import pdb
import sys
import os
import logging
import argparse
import SocketServer
import json
import time


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
                       Customer009,Customer011,Customer012,Customer013,Customer014) \
                       values (@hostid + 1,%(Cpu)s,now(),'%(DeviceClass)s','%(HostName)s','%(InnerIP)s','%(Mem)s',\
                       '%(OSName)s','%(Region)s','%(Customer010)s','1','在线','%(Customer001)s','%(Customer002)s',\
                       '%(Customer004)s','%(Customer005)s','%(Customer008)s','%(Customer009)s','%(Customer011)s',\
                       '%(Customer012)s','%(Customer013)s','%(Customer014)s')" \
                       % {"Cpu": sdata['cpu_num'], "DeviceClass": sdata['Product'], "HostName": sdata['hostname'], \
                       "InnerIP": sdata['inip'], "Mem": sdata['memory'], "OSName": sdata['version'], \
                       "Region": sdata['city'], "Customer010": sdata['SN'], "Customer001": sdata['vip'], \
                       "Customer002": sdata['disk_sum'], "Customer004": sdata['bip'], "Customer005": \
                       sdata['vpn'], "Customer008": sdata['idcname'], "Customer009": sdata['disk_num'], \
                       "Customer011": sdata['cpu_rate'], "Customer012": sdata['mem_rate'], "Customer013": sdata['disk_rate'], \
                       "Customer014": sdata['start_time']})

        cursor.execute("set @newid = (select HostID from cmdb.cc_HostBase where InnerIP='%s')" % sdata['inip'])

        cursor.execute('insert into cmdb.cc_ModuleHostConfig (ID,ApplicationID,HostID,ModuleID,SetID) values (@id + 1,1,@newid,1,1)')

    else:
        cursor.execute("update cmdb.cc_HostBase set DeviceClass='%(DeviceClass)s',Cpu=%(Cpu)s,\
                       Mem=%(Mem)s,OSName='%(OSName)s',Region='%(Region)s',\
                       Customer002='%(Customer002)s',Customer008='%(Customer008)s',\
                       Customer009='%(Customer009)s',Customer010='%(Customer010)s',Customer011='%(Customer011)s',\
                       Customer012='%(Customer012)s',Customer013='%(Customer013)s',Customer014='%(Customer014)s' \
                       where InnerIP='%(InnerIP)s'" % {"Cpu": sdata['cpu_num'], "DeviceClass": sdata['Product'], \
                       "InnerIP": sdata['inip'], "Mem": sdata['memory'], "OSName": sdata['version'], \
                       "Region": sdata['city'], "Customer010": sdata['SN'], \
                       "Customer002": sdata['disk_sum'], "Customer008": sdata['idcname'], \
                       "Customer009": sdata['disk_num'], "Customer011": sdata['cpu_rate'], "Customer012": sdata['mem_rate'], \
                       "Customer013": sdata['disk_rate'], "Customer014": sdata['start_time']})
    db.commit()
    db.close()

def start_message(bindport, bindip):
    print "Server is starting"
    print "Server is listenting port %s, bind %s" % (bindport, bindip)
    return 0

def data_json():
    def disk_used():
        used = data['disk_rate'].split()
        used_data = []
        used_data.append(used[0].strip('%'))
        used_data.append(used[1].strip('G'))
        return used_data

    def mem_used():
        used = data['mem_rate'].split()
        used_data = []
        used_data.append(used[0].strip('%'))
        used_data.append(used[1].strip('G'))
        return used_data
    

    cmdb_dict = {}
    cmdb_dict['city'] = data['city']
    cmdb_dict['disk_num'] = data['disk_num']
    cmdb_dict['disk_rate'] = float(disk_used()[0])
    cmdb_dict['disk_used'] = float(disk_used()[1])
    cmdb_dict['cpu_num'] = data['cpu_num']
    cmdb_dict['ip'] = data['inip']
    cmdb_dict['start_time'] = data['start_time']
    try:
        cmdb_dict['Product'] = data['Product']
    except:
        logging.error('data keyerror')
        cmdb_dict['Product'] = ''
    cmdb_dict['cpu_rate'] = float(data['cpu_rate'].strip('%'))
    cmdb_dict['mem_rate'] = float(mem_used()[0])
    cmdb_dict['mem_used'] = float(mem_used()[1])
    cmdb_dict['version'] = data['version']
    cmdb_dict['memory'] = int(data['memory'])
    cmdb_dict['disk_sum'] = float(data['disk_sum'].strip('G'))
    return cmdb_dict



class CMDBServer(SocketServer.BaseRequestHandler):
    def handle(self):
        conn = self.request
        global data
        agentdata = conn.recv(1048576)
        time.sleep(3)
        while True:
            if not agentdata:
                break
            else:
                try:
                    data = json.loads(agentdata, encoding='utf-8')
                except:
                    logging.error('Get data is failed')
                try:
                    cmdbdata = data_json()
                    cmdb_data = json.dumps(cmdbdata, ensure_ascii=False, encoding='utf-8')
                except:
                    logging.error(data['inip'] + ' ' + 'data key value is Failed')
                try:
                    cmdblog = open('data/cmdb_data.log', 'a+')
                    cmdblog.write(cmdb_data + '\n')
                    cmdblog.flush()
                    cmdblog.close()
                except:
                    logging.error('The file or directory cannot be not found')
                try:
                    mysqlconnt(data, get_conf('dbserver'), get_conf('dbuser'), get_conf('dbpasswd') ,'cmdb')
                except:
                    logging.error(data['inip'] + ' ' + 'Failed to write data to the database')
            break

if __name__ == '__main__':
    var = sys.argv[1]
    if var == 'start':
        start_message(get_conf('bindport'), get_conf('bindip'))
        datapath = os.path.isdir('data')
        if datapath == False:
            os.mkdir('data')
        server = SocketServer.ThreadingTCPServer((get_conf('bindip'), int(get_conf('bindport'))),CMDBServer)
        server.serve_forever()
    elif var == 'stop':
        print "CMDB DATA Server closing....."
        time.sleep(1)
        os.system("ps -ef |grep cmdbserver |grep -v grep |awk '{print $2}' |xargs kill -9")     
