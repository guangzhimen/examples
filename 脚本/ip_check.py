#!/usr/local/bin/python3.6
#coding:utf-8
from multiprocessing import Pool
import os

put = raw_input("input you check network ip : ")
down = open('ip_down.log','w')
up = open('ip_up.log','w')

def vol_ip():
  network = put
  data = network.split('.')
  ip_list = []
  for i in range(1, 255):
      ip = str(data[0] + '.' + data[1] + '.' + data[2] + '.' + str(i))
      ip_list.append(ip)

  return ip_list

def pingip(ip_out):
    value = os.system('ping -c1 -t1 %s > /dev/null' % ip_out)
    out_id = value
    if out_id != 0:
       down.write(str(ip_out + '\n'))
       print ip_out + '\033[1;31;40m down \033[0m'
    else:
       up.write(str(ip_out + '\n'))
       print ip_out + '\033[1;32;40m up \033[0m'

    down.flush()
    up.flush()
    return 0

if __name__ == '__main__':
    pool = Pool(25)
    for ip_id in vol_ip():
        pool.apply_async(pingip, (ip_id,))
    pool.close()
    pool.join()
    down.close()
    up.close()
