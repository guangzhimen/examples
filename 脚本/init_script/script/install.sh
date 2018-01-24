#!/bin/bash
path="/apps/mysql"
path_data="/apps/data/axon"

mkdir -p $path/run
mkdir -p $path/log
mkdir -p $path_data

chown -Rf mysql:mysql $path
chgrp -R mysql $path
chown -R root $path
chown -R mysql $path_data
chown -R mysql $path/run/
chown -R mysql $apth/log/

cp $path/mysql.service /lib/systemd/system
chmod 755 /etc/init.d/mysql

ln -s $path /usr/local/mysql

$path/bin/mysqld --initialize-insecure --user=mysql --basedir=$path/ --datadir=$path_data >/dev/null 2>&1
$path/bin/mysql_ssl_rsa_setup --datadir=$path_data >/dev/null 2>&1

exit 0
