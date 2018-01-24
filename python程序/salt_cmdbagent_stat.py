#!/usr/bin/python
#coding=utf-8
from subprocess import Popen, PIPE
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import sys

reload(sys)
sys.setdefaultencoding( "utf-8" )

#smtp发送邮件模块
def mail(cmdb, salt, cmdbwin, saltwin):
    sender = 'xxxxx'
    receiver = 'xxxxx'
    subject = 'CMDB客户端状态监控'
    smtpserver = 'smtp.qiye.163.com'
    username = 'xxxxx'
    password = 'xxxxx'
    
    message = 'Linux服务器：\nCMDB Agent 失去连接：\n%(cmdb)s\nSalt Agent 失去连接：\n%(salt)s\n\n \
Windows服务器：\nCMDB Agent 失去连接：\n%(cmdbwin)s\nSalt Agent 失去连接：\n%(saltwin)s\n' % \
               {"cmdb": cmdb, "salt": salt, "cmdbwin": cmdbwin, "saltwin": saltwin}

    msg = MIMEText(message,'plain','utf-8')
#    msg['From'] = Header(sender, 'utf-8')
#    msg['To'] =  Header(receiver, 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')

    smtp = smtplib.SMTP()
    smtp.connect(smtpserver, 25)
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()

#使用salt检测linux下的cmdb客户端的进程是否存在，（里面涉及list数据类型转换为dict类型的方法）
def cmdrun():
    keys, value = [], []
    p = Popen("salt 'linux-*' cmd.run 'ps -ef |grep cmdbagent |grep -v grep |wc -l'", stdout = PIPE, stderr = PIPE, shell=True)
    stdout = list(p.communicate())
    key = stdout[0]
#以下是list格式转为dict格式的过程，更具list内元素分布的不同，使用不同的过滤条件
    filterd = [i for i in key.split('\n')]
    for i in range(len(filterd)):
        if (i % 2) == 0:
            keys.append(filterd[i])
        else:
            value.append(filterd[i])
    lsalt = dict(zip(keys, value))
    return lsalt

#使用salt检测windows下的cmdb客户端的进程是否存在，（里面涉及list数据类型转换为dict类型的方法，涉及删除list中指定的重复元素的方法）
def wincmdrun():
    keys, value = [], []
    p = Popen("""salt '1*' cmd.run 'tasklist |findstr cmdbagent |find /C "exe"'""", stdout = PIPE, stderr = PIPE, shell=True)
    stdout = list(p.communicate())
    key = stdout[0]
    filterd = [i for i in key.split('\n')]
#以下是删除list中指定的重复元素的方法
    del_one = "    'chcp' ²»ÊÇÄÚ²¿»òÍâ²¿ÃüÁî£¬Ò²²»ÊÇ¿ÉÔËÐÐµÄ³ÌÐò"
    del_two = "    »òÅú´¦ÀíÎÄ¼þ¡£"
    while del_one in filterd:
        filterd.remove(del_one)
    while del_two in filterd:
        filterd.remove(del_two)
#以下是list格式转为dict格式的过程，更具list内元素分布的不同，使用不同的过滤条件
    for i in range(len(filterd)):
        if (i % 2) == 0:
            keys.append(filterd[i])
        else:
            value.append(filterd[i])
    winsalt = dict(zip(keys, value))
    return winsalt

#把上面函数返回的dict格式的数据，重新格式成易于人类查看的邮件文本模板（linux）      
def getdata(data):
    cmdb_li = []
    salt_li = []
    for i in data:
        if data[i].strip() < '2':
            cmdb_li.append("       %s  cmdbagent down!" % i)
        elif data[i].find('Minion did not return') == 4:
            salt_li.append("       %s  salt down!" % i)
#以下涉及把格式化list转为tuple，然后使用join函数用换行符分割tuple，然后转换成str格式
    joincmdb = '\n'.join(tuple(cmdb_li))
    joinsalt = '\n'.join(tuple(salt_li))
    return joincmdb, joinsalt

#把上面函数返回的dict格式的数据，重新格式成易于人类查看的邮件文本模板（windows）
def wingetdata(data):
    wincmdb_li = []
    winsalt_li = []
    for i in data:
        if data[i].strip() < '2':
            wincmdb_li.append("       %s  cmdbagent down!" % i)
        elif data[i].find('Minion did not return') == 4:
            winsalt_li.append("       %s  salt down!" % i)
    w_joincmdb = '\n'.join(tuple(wincmdb_li))
    w_joinsalt = '\n'.join(tuple(winsalt_li))
    return w_joincmdb, w_joinsalt

#主函数，用个调用定义的发送邮件函数，然后格式化需要发送邮件的内容
def main():
    sedmail = mail(list(getdata(cmdrun()))[0], list(getdata(cmdrun()))[1], list(wingetdata(wincmdrun()))[0], list(wingetdata(wincmdrun()))[1])
    return sedmail

#执行主函数
if __name__ == "__main__":
    main()
