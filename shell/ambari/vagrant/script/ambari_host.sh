#!/bin/sh

source /vagrant/config/config.sh

##############################################################################################
#dns config
echo 'modify dns config'
sudo sed -i "/plugins/a\dns=none" /etc/NetworkManager/NetworkManager.conf 
sudo systemctl restart NetworkManager.service

sudo sed -i "/nameserver/d" /etc/resolv.conf
echo 'modify resolv.conf'
cat << EOF | sudo tee -a /etc/resolv.conf
search $DOMAIN
nameserver $REPO_HOST
nameserver $PUBLIC_DNS
EOF
cat /etc/resolv.conf

echo "cancel hostname in /etc/hosts"
sudo sed -i "/127.0.0.1.*$DOMAIN.*/d" /etc/hosts

ping repo.$DOMAIN -c 1


##############################################################################################
## do install after dns complete
source /vagrant/script/repo/local_proxy.sh
source /vagrant/script/repo/install.sh


##############################################################################################
echo "set ntp client"
sudo yum install -y ntp ntpdate

sudo sh -c "echo 'SYNC_HWCLOCK=yes' >>/etc/sysconfig/ntpd"
sudo sed -i 's/\(server [0-3]\)/# \1/g' /etc/ntp.conf
sudo sed -i "/server 0/i\server $REPO_HOST prefer" /etc/ntp.conf
sudo sed -i "/server 3/a\ \nserver  127.127.1.0\nfudge   127.127.1.0 stratum 10" /etc/ntp.conf

sudo systemctl restart ntpd.service
sudo systemctl enable ntpd.service




