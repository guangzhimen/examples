#!/bin/bash

for index in `curl -s -XGET http://192.168.1.49:9200/_cat/shards | grep UNASSIGNED | awk '{print $1}' |uniq`
do
    for shard in `curl -s -XGET http://192.168.1.49:9200/_cat/shards | grep $index | grep UNASSIGNED |awk '{print $2}'`
    do
        for node in `curl -s -XGET http://192.168.1.49:9200/_cat/shards | grep $index | grep "$shard p" |awk '{print $8}'`
        do
           if [ $node == "" ]; then
           curl -s -XPOST http://192.168.1.49:9200/_cluster/reroute?pretty -d '{ "commands" : [ { "move" : { "index" : "'"$index"'", "shard" : "'$shard'", "from_node" : "node-3", "to_node" : "node-2" } } ] }' > /dev/null
           elif [ $node == "node-3" ]; then
           curl -s -XPOST http://192.168.1.49:9200/_cluster/reroute?pretty -d '{ "commands" : [ { "move" : { "index" : "'"$index"'", "shard" : '"$shard"', "from_node" : "'"$node"'", "to_node" : "node-1" } }, { "allocate_replica" : { "index" : "'"$index"'", "shard" : '"$shard"', "node" : "node-2" } } ] }' > /dev/null
           elif [ $node == "node-2" ]; then
           curl -s -XPOST http://192.168.1.49:9200/_cluster/reroute?pretty -d '{ "commands" : [ { "move" : { "index" : "'"$index"'", "shard" : '"$shard"', "from_node" : "'"$node"'", "to_node" : "node-1" } }, { "allocate_replica" : { "index" : "'"$index"'", "shard" : '"$shard"', "node" : "node-3" } } ] }' > /dev/null
           elif [ $node == "node-1" ]; then
           curl -s -XPOST http://192.168.1.49:9200/_cluster/reroute?pretty -d '{ "commands" : [ { "move" : { "index" : "'"$index"'", "shard" : '"$shard"', "from_node" : "'"$node"'", "to_node" : "node-2" } }, { "allocate_replica" : { "index" : "'"$index"'", "shard" : '"$shard"', "node" : "node-3" } } ] }' > /dev/null
fi
       done
    done
done         


