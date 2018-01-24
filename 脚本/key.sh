#!/bin/bash
key=`curl http://10.10.141.38/1.txt`
echo "$key" | base64 -i
