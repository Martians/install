
#!/usr/bin/env bash

source config.sh

##########################################################################
##########################################################################
#repo config
echo 'modify repo config'
sudo mv /etc/yum.repos.d /etc/yum.repos.d.bak
sudo mkdir /etc/yum.repos.d
cp /vagrant/config/ambari-2.5.2.0.repo /etc/yum.repos.d/ambari.repo
cp /vagrant/config/CentOS7-Base-aliyun.repo /etc/yum.repos.d/

#yum cache
echo 'update yum cache'
sudo yum clean all
sudo yum repolist

#install tools
echo 'install all tools'
sudo yum install tree -y
sudo yum install wget -y
sudo yum install yum-utils -y
sudo yum install bash-completion -y


##########################################################################
##########################################################################
#stop firewalld
echo 'stop firewalld and selinux'
sudo systemctl stop firewalld.service
sudo systemctl disable firewalld.service
setenforce 0
sudo sed -i 's/SELINUX=.*/SELINUX=disabled/' /etc/selinux/config

#ntp config
echo 'ntp client config'
sudo yum install ntp -y
sudo sed -i 's/server [0-3].centos.*/server $repo_host/' /etc/ntp.conf
sudo systemctl start ntpd.service
sudo systemctl enable ntpd.service
sudo timedatectl set-ntp yes

#conflict resolution
echo 'conflict resolution'
sudo yum erase -y snappy.x86_64
sudo systemctl stop chronyd.service
sudo systemctl disable chronyd.service
sudo systemctl restart ntpd.service

ntpdate -u $repo_host
ntpq -p

#Increasing swap space
echo 'swap config'
sudo dd if=/dev/zero of=/swapfile bs=1024 count=1024k
sudo mkswap /swapfile
sudo swapon /swapfile
echo "/swapfile       none    swap    sw      0       0" >> /etc/fstab


##########################################################################
##########################################################################
#ssh login config
echo 'ssh login config'
wget -N -P /tmp/ http://$repo_host/resource/ssh.tar.gz
tar -zxvf /tmp/ssh.tar.gz -C /tmp/

sudo mkdir -p /root/.ssh
sudo cp /tmp/ssh/id_rsa /tmp/ssh/id_rsa.pub /root/.ssh/
sudo cp /tmp/ssh/id_rsa /tmp/ssh/id_rsa /root/.ssh/
sudo cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys
sudo chmod 600 /root/.ssh/*;


#hostname, ipaddr and add disk
wget -N -P /tmp/ http://$repo_host/resource/script.tar.gz
tar -zxvf /tmp/script.tar.gz -C /tmp/
#. /tmp/script/hostname_set.sh
#. /tmp/script/ipaddr_set.sh
#. /tmp/script/add_disk.sh

#network restart
sudo service network restart
