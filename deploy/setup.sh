#!/bin/bash
echo "安装将花费一定时间，请耐心等待直到安装完成^_^, ..."
sudo apt-get update
sudo apt-get install -y python-setuptools python-dev git easy_install pip docker-engine

cd /home && sudo rm -rf opentech
sudo mkdir opentech && cd opentech
sudo git clone https://github.com/msopentechcn/open-hackathon.git
cd /home/opentech/open-hackathon
sudo pip install -r open-hackathon-server/requirement.txt
sudo pip install -r open-hackathon-client/requirement.txt
sudo cp open-hackathon-server/src/hackathon/config_sample.py open-hackathon-server/src/hackathon/config.py
sudo cp open-hackathon-server/src/hackathon/config_sample.py open-hackathon-server/src/hackathon/config.py

# install and Configure guacamole
sudo apt-get install -y libcairo2-dev libjpeg62-turbo-dev libjpeg62-dev libpng12-dev libossp-uuid-dev
sudo apt-get install -y libfreerdp-dev libpango1.0-dev libssh2-1-dev libtelnet-dev
sudo apt-get install -y libvncserver-dev libwebp-dev libssl-dev libvorbis-dev
cd /home/opentech && sudo wget http://sourceforge.net/projects/guacamole/files/current/source/guacamole-server-0.9.9.tar.gz/download
sudo mv download guacamole-server-0.9.9.tar.gz && sudo tar -xzf guacamole-server-0.9.9.tar.gz && cd guacamole-server-0.9.9/
sudo autoreconf -fi
sudo ./configure --with-init-dir=/etc/init.d
sudo make
sudo make install
# configure guacamole client
sudo wget http://sourceforge.net/projects/guacamole/files/current/binary/guacamole-0.9.9.war/download
sudo mv download /var/lib/tomcat7/webapps/guacamole.war
# configure guacamole authentication provider
sudo mkdir /usr/share/tomcat7/.guacamole
sudo mkdir /etc/guacamole
cd /home/opentech/open-hackathon/deploy/guacamole
cp guacamole-sample.properties /etc/guacamole/guacamole.properties
cp *.jar /etc/guacamole
sudo ln -s /etc/guacamole/guacamole.properties /usr/share/tomcat7/.guacamole/guacamole.properties


# install docker
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
# get ubuntu version
# for ubuntu 14
uversion=$(lsb_release -d | grep 14)
if [ ${uversion} > 0 ]; then
    sudo echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" > /etc/apt/sources.list.d/docker.list
fi

# for ubuntu 15
uversion=$(lsb_release -d | grep 15)
if [ ${uversion} > 0 ]; then
    sudo echo "deb https://apt.dockerproject.org/repo ubuntu-wily main" > /etc/apt/sources.list.d/docker.list
fi

sudo apt-get update
sudo apt-get purge lxc-docker
sudo apt-cache policy docker-engine
sudo apt-get update
# for ubuntu 15
sudo apt-get install linux-image-extra-$(uname -r)
# for ubuntu 12 & 14
sudo apt-get install apparmor
sudo apt-get install docker-engine
sudo service docker start
sudo docker run hello-world

sudo usermod -aG docker ubuntu

sudo groupadd docker
sudo gpasswd -a ${USER} docker

sudo docker pull rastasheep/ubuntu-sshd
# Logging && Hosts
sudo mkdir /var/log/open-hackathon
sudo chmod -R 644 /var/log/open-hackathon

if grep -qs "open-hackathon-dev.chinacloudapp.cn" /etc/hosts; then
    echo "127.0.0.1 open-hackathon-dev.chinacloudapp.cn" >> /etc/hosts
fi

# Installing uWSGI
sudo pip install uwsgi

