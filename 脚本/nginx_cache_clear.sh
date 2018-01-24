#!/bin/bash
dir=`pwd`
key=`$dir/key | base64 -d`
file=`pwd`/pass.sh
cat  << EOF > pass.sh
#!/bin/bash
echo "$key"
EOF
chmod 755 pass.sh
echo "echo [ putting.... ]; sh /apps/usr/nginx/clear_nginx_cache.sh" | setsid env SSH_ASKPASS="`pwd`/pass.sh" DISPLAY="none:0" ssh root@192.200.154.48 2>&1
if [ -e $flie ]; then
        rm -rf $file
fi
