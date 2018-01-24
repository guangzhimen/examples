#coding:utf-8

import os
import sys

print "input network ip : "

ip = raw_input()

data = ip.split('.')

num1 = data[0]
num2 = data[1]
num3 = data[2]

ip_list = []
file = open('/apps/home/ansible/log/ip_down.log','w')

for i in range(1, 255):
    x = str(num1 + '.' + num2 + '.' + num3 + '.' + str(i))
    ip_list.append(x)
for n in ip_list:
    out_id = os.system('ping -c1 -w1 %s > /dev/null'%n)
    if out_id != 0:
        file.write(str(n + '\n'))
	print n + '\033[1;31;40m down \033[0m'
    else:
	print n + '\033[1;32;40m up \033[0m'

#threading.Thread(target = PING,args = (),name = 'thread-' + str(t)).start()

file.close()
sys.exit()
