#!/usr/bin/python
#coding=utf-8
import pexpect
from subprocess import Popen, PIPE
import sys

reload(sys)
sys.setdefaultencoding( "utf-8" )


def dell_ipmi(ip, user, passwd, cmd):
    child = pexpect.spawn('ssh %s@%s %s' % (user, ip, cmd))
    if child.expect([pexpect.TIMEOUT, ".*Are you sure you want to continue connecting (yes/no)?.*"]):
        child.sendline('yes')
        child.expect('.*password.*')
        child.sendline(passwd)
    elif child.expect([pexpect.TIMEOUT, '.*password.*']):
        child.sendline(passwd)
    child.expect(pexpect.EOF)
    print(child.before)

def supercould_ipmi(ip):
    p = Popen("ipmitool -H %s -U ADMIN -P ADMIN power reset" % ip, stdout = PIPE, stderr = PIPE, shell=True)
    stdout, stderr = p.communicate()
    return stdout

if __name__ == "__main__":
    if sys.argv[4] == 'dell':
        dell_ipmi(sys.argv[1], sys.argv[2], sys.argv[3], "racadm serveraction powercycle")
    elif sys.argv[4] == 'super':
        supercould_ipmi(sys.argv[1])
