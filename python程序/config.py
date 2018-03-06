#coding=utf-8
# axon-elk

interval = 60 # 上报的 step 间隔
exs = 2 #主机数量
server = "127.0.0.1" #logstash服务器地址
port = "5044"        #logstash上tcp服务的端口号


exsi1 = ["10.10.188.201", "root", "123456"] #exsi主机的ip，账号，密码
exsi2 = ["10.10.188.202", "root", "123456"] #复数exsi主机配置

