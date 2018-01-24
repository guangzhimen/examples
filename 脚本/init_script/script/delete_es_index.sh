#!/bin/bash
curl -XDELETE http://192.168.1.49:9200/logstash-flow*
val=`curl http://192.168.1.49:9200/logstash-flow* | wc -l`
if [ $val -eq 0 ]; then
	break
else
	curl -XDELETE http://192.168.1.49:9200/logstash-flow*
fi
