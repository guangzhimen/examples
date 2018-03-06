#!/usr/bin/env python
#coding=utf-8 

import atexit
from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnectNoSSL, Disconnect
import sys
import time
import json
import config
from datetime import timedelta
import logging
import socket


logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%d %b %Y %H:%M:%S',
                    filename='error.log',
                    filemode='a+')


def HostInformation(host,datacenter_name,computeResource_name,content,perf_dict,vchtime,interval,exsi):
    try:
        statInt = interval/20
        summary = host.summary
        stats = summary.quickStats
        hardware = host.hardware

        tags = "host=" + str(exsi)
        data['tag'] = tags

        uptime = stats.uptime
        data['esxi.uptime'] = uptime

        cpuUsage = 100 * 1000 * 1000 * float(stats.overallCpuUsage) / float(hardware.cpuInfo.numCpuCores * hardware.cpuInfo.hz)
        data['esxi.cpu.usage'] = float('%.2f' % cpuUsage)

        memoryCapacity = float(hardware.memorySize) / (1024**3)
        data['esxi.memory.capacity'] = float('%.2f' % memoryCapacity)

        memoryUsage = float(stats.overallMemoryUsage / 1024)
        data['esxi.memory.usage'] = memoryUsage

        freeMemoryPercentage = float('%.2f' % (100 - ((float(memoryUsage) / memoryCapacity) * 100)))
        data['esxi.memory.freePercent'] = freeMemoryPercentage

        statdiskwiteio = BuildQuery(content, vchtime, perf_dict['disk.write.average'], "", host, interval)
        diskwiteio = float('%.2f' % ((float(statdiskwiteio[0].value[0].value[0] * 1024) / statInt) / 1024))
        data['esxi.disk.iowite'] = diskwiteio
        
        statdiskreadio = BuildQuery(content, vchtime, perf_dict['disk.read.average'], "", host, interval)
        diskreadio = float('%.2f' % ((float(statdiskreadio[0].value[0].value[0] * 1024) / statInt) / 1024))
        data['esxi.disk.ioread'] = diskreadio

        statNetworkTx = BuildQuery(content, vchtime, perf_dict['net.transmitted.average'], "", host, interval)
        networkTx = float('%.2f' % ((float(statNetworkTx[0].value[0].value[0] * 8 * 1024) / statInt) / 1024))
        data['esxi.net.if.out'] = networkTx
        
        statNetworkRx = BuildQuery(content, vchtime, perf_dict['net.received.average'], "", host, interval)
        networkRx = float('%.2f' % ((float(statNetworkRx[0].value[0].value[0] * 8 * 1024) / statInt) / 1024))
        data['esxi.net.if.in'] = networkRx

    except Exception as error:
        print "Unable to access information for host: ", str(exsi)
        print error
        pass


def ComputeResourceInformation(computeResource,datacenter_name,content,perf_dict,vchtime,interval,exsi):
    try:
        hostList = computeResource.host
        computeResource_name = computeResource.name
        for host in hostList:
            HostInformation(host,datacenter_name,computeResource_name,content,perf_dict,vchtime,interval,exsi)
    except Exception as error:
        print "Unable to access information for compute resource: ", 
        computeResource.name
        print error
        pass

def DatastoreInformation(datastore,datacenter_name):
    try:
        summary = datastore.summary
        name = summary.name
        TYPE = summary.type

        capacity = float(summary.capacity) / (1024**3)
        data['datastore.capacity'] = float('%.2f' % capacity)

        freeSpace = float(summary.freeSpace) / (1024**3)
        data['datastore.free'] = float('%.2f' % freeSpace)
        
        uncommitted = float(summary.uncommitted) / (1024**3)
        data['datastore.committed'] = float('%.2f' % uncommitted)

        freeSpacePercentage = (float(freeSpace) / capacity) * 100
        data['datastore.freePercent'] = float('%.2f' % freeSpacePercentage)
        
    except Exception as error:
        print "Unable to access summary for datastore: ", datastore.name
        print error
        pass


def run(exsi,user,pwd,interval):
    try:
        si = SmartConnectNoSSL(host=exsi, user=user, pwd=pwd, port=443)
        atexit.register(Disconnect, si)
        content = si.RetrieveContent()
        vchtime = si.CurrentTime()

        perf_dict = {}
        perfList = content.perfManager.perfCounter
        for counter in perfList:
            counter_full = "{}.{}.{}".format(counter.groupInfo.key, counter.nameInfo.key, counter.rollupType)
            perf_dict[counter_full] = counter.key
        
        for datacenter in content.rootFolder.childEntity:
            datacenter_name = datacenter.name.encode("utf8")
            datastores = datacenter.datastore
            for ds in datastores:
                DatastoreInformation(ds,datacenter_name)

            if hasattr(datacenter.hostFolder, 'childEntity'):
                hostFolder = datacenter.hostFolder
                computeResourceList = []
                computeResourceList = getComputeResource(hostFolder,computeResourceList)
                for computeResource in computeResourceList:
                    ComputeResourceInformation(computeResource,datacenter_name,content,perf_dict,vchtime,interval,exsi)

    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return False, error.msg
    return True, "ok"

def getComputeResource(Folder,computeResourceList):
    if hasattr(Folder, 'childEntity'):
        for computeResource in Folder.childEntity:
           getComputeResource(computeResource,computeResourceList)
    else:
        computeResourceList.append(Folder)
    return computeResourceList

def hello_vcenter(vchost,username,password):
    try:
        si = SmartConnectNoSSL(
            host=vchost,
            user=username,
            pwd=password,
            port=443)

        atexit.register(Disconnect, si)
        return True, "ok"
    except vmodl.MethodFault as error:
        return False, error.msg
    except Exception as e:
        return False, str(e)


def BuildQuery(content, vchtime, counterId, instance, entity, interval):
    perfManager = content.perfManager
    metricId = vim.PerformanceManager.MetricId(counterId=counterId, instance=instance)
    startTime = vchtime - timedelta(seconds=(interval + 60))
    endTime = vchtime - timedelta(seconds=60)
    query = vim.PerformanceManager.QuerySpec(intervalId=20, entity=entity, metricId=[metricId], startTime=startTime,
                                             endTime=endTime)
    perfResults = perfManager.QueryPerf(querySpec=[query])
    if perfResults:
        return perfResults
    else:
        return False

def post_socket(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((str(config.server), int(config.port)))
        sock.sendall(json.dumps(data, ensure_ascii=False, encoding='utf-8'))
    except socket.error:
        logging.error('[Errno 111]' + ' ' + "127.0.0.1" + ':' + "5044" + ' ' + 'Connection refused')
    sock.close()
    

if __name__ == "__main__":
    interval = config.interval
    ts = int(time.time())
    exsilist = [ "config.exsi" + str(sum+1) for sum in range(config.exs) ]
    for exsisum in exsilist:
        exsi = eval(exsisum)[0]
        user = eval(exsisum)[1]
        pwd = eval(exsisum)[2]
        data = {}
        success, msg = hello_vcenter(exsi,user,pwd)
        if success == False:
            print msg
            data['vcenter.alive'] = 0
#            print json.dumps(data,indent=4)
            sys.exit(1)
            data['vcenter.alive'] = 1
        run(exsi,user,pwd,interval)
        if sys.argv[-1] == "print":
            print json.dumps(data,indent=4)
        elif sys.argv[-1] == "post":
            post_socket(data)
