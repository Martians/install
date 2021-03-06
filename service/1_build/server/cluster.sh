#!/bin/bash

# note: run when docker start

BASE_PATH=$(cd "$(dirname "$0")"; cd ../..; pwd)
cd $BASE_PATH

. 0_config/config.sh

# 目前通过dns来配置，就不需要硬编码了

##############################################################
# 方式1：使用临时文件，添加/etc/hosts
# HOST1=$(alloc_host 1)
# HOST2=$(alloc_host 2)
# HOST3=$(alloc_host 3)

# # /etc/host文件是挂载到docker中的，不能直接使用sed，它会删除并重建文件
# TEMP=/tmp/hosts_tmp
# \cp /etc/hosts $TEMP
# sed -i "/sshd-*/d" $TEMP

# # 添加cluster中的映射
# echo "
# $HOST1  sshd-1
# $HOST2 	sshd-2
# $HOST3 	sshd-3
# " >> $TEMP
# cat $TEMP > /etc/hosts

##############################################################
# 方式2：使用内存变量，修改dns
# exist="$(cat /etc/resolv.conf)"
# echo "nameserver $(alloc_host DNS)" > /etc/resolv.conf 
# echo "$exist" >> /etc/resolv.conf 
# cat /etc/resolv.conf 


