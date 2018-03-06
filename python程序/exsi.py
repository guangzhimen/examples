#!/usr/bin/env python
#coding=utf-8

import json
from pyVim import connect
from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import atexit
import sys


reload(sys)
sys.setdefaultencoding( "utf-8" )


def printinfo(ip, user, passwd):
    hosts = []

    def vminfo(vm):
        summary = vm.summary
        hosts.append(summary.config.name)
        hosts.append(summary.config.vmPathName)
        hosts.append(summary.config.guestFullName)
        hosts.append(summary.runtime.powerState)
        hosts.append(summary.config.instanceUuid) 

    my_exsi = SmartConnectNoSSL(host = ip, port = 443, user = user, pwd = passwd)
    atexit.register(connect.Disconnect, my_exsi)
    content = my_exsi.RetrieveContent()
    container = content.rootFolder
    viewType = [vim.VirtualMachine]
    containerView = content.viewManager.CreateContainerView(container, viewType, True)
    children = containerView.view
    for vm in children:
        vminfo(vm)
    return hosts

def data(vmdata):
    info = vmdata
    j = 0
    list_host = []
    for x in range(len(info)):
        if j < len(info): 
            dist_host = {}
            for i in range(j, j+5):
                dist_host['storage_name'] = info[i-3]
                dist_host['operating_system'] = info[i-2]
                dist_host['power_state'] = info[i-1]
                dist_host['name'] = info[i-4]
                dist_host['uuid'] = info[i]
            list_host.append(dist_host)
            j += 5
    return list_host

def reboot_vm(ip, user, passwd, uuid):
    my_exsi = None
    my_exsi = SmartConnectNoSSL(host = ip, port = 443, user = user, pwd = passwd)
    vm = my_exsi.content.searchIndex.FindByUuid(None, uuid, True, True)
    try:
        vm.RebootGuest()
    except:
        vm.ResetVM_Task()
    Disconnect(my_exsi)

if __name__ == "__main__":
    if sys.argv[1] == 'print':
        result = data(printinfo("10.10.188.201", "root", "123456"))
        for i in range(len(result)):
            print("name               : " + result[i]['name'])
            print("uuid               : " + result[i]['uuid'])
            print("Power State        : " + result[i]['power_state'])
            print("Operating System   : " + result[i]['operating_system'])
            print("Storage Name       : " + result[i]['storage_name'])
            print "-------------------- "
    elif sys.argv[1] == 'reboot':
        if not reboot_vm("10.10.188.201", "root", "axon@234", sys.argv[2]):
            print "vm reboot is Success"
        else:
            print "reboot is fail !"
