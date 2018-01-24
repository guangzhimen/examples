#!/bin/bash
#17-12-1

source /etc/profile

svn_dir=/apps/svn/yunwei
svn_backup_dir=/apps/nfs/yumwei_repo
log_dir=/apps/svn

ls $svn_backup_dir > /dev/unll
if [ $? -eq 0 ]; then
  svnadmin dump $svn_dir > $svn_vackup_dir/yunwei_backup_`date +%y%m%d`
  if [ $? -eq 0 ]; then
    find $svn_backup_dir -atime +1 -exec rm -rf {} \;
    echo "`date +%Y-%D-%T`  success svn 备份成功。" >> $log_dir/svn_backup.log
  else
    echo "`date +%Y-%D-%T`  error 备份文件时出现异常，请排查！" >> $log_dir/svn_backup.log
  fi
else
  echo "`date +%Y-%D-%T`  error 目录不存在，备份失败！" >> $log_dir/svn_backup.log
fi
