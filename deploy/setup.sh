#!/bin/bash

get_dependency_software() {
    echo "updating apt-get......"
    result=$( apt-get update)
    if grep -q "Could not resolve" <<< $result; then
        echo "Could not update apt-get, please solve it"
        exit
    fi
    echo "installing git python-setuptools python-dev python-pip"
    result=$( apt-get install -y git python-setuptools python-dev python-pip)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software, pls install docker manually"
        exit
    fi
    echo "installing autoconf libtool tomcat7 mongodb"
    result=$( apt-get install -y autoconf automake libtool tomcat7 mongodb)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software, pls install docker manually"
        exit
    fi
}

set_envirement() {
    cd /home &&  rm -rf opentech
    mkdir opentech && cd opentech
    rm -r open-hackathon
    echo "git cloning open-hackathon source code"
    result=$( git clone https://github.com/YaningX/open-hackathon.git)
    if grep -q "unable to access" <<< $result; then
        echo "Could not git clone open-hackathon source code, pls check your network"
        exit
    fi
    cd /home/opentech/open-hackathon
    echo "pip is installing required python library"
    result=$( pip install -r open-hackathon-server/requirement.txt)

    result=$( pip install -r open-hackathon-client/requirement.txt)
    cp open-hackathon-server/src/hackathon/config_sample.py open-hackathon-server/src/hackathon/config.py
    cp open-hackathon-server/src/hackathon/config_sample.py open-hackathon-server/src/hackathon/config.py
}

get_dependency_for_guacamole() {
    result=$(sudo service guacd restart)
    if grep -q "SUCCESS" <<< $result; then
        echo "guacamole is installed!"
        return
    fi
    echo "installing libcairo2-dev"
    result=$( apt-get install -y libcairo2-dev)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software for guacamole, pls install guacamole manually"
        exit
    fi
    echo "installing libjpeg62-dev libpng12-dev libossp-uuid-dev"
    result=$( apt-get install -y libjpeg62-dev libpng12-dev libossp-uuid-dev)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software for guacamole, pls install guacamole manually"
        exit
    fi
    echo "installing libfreerdp-dev libpango1.0-dev libssh2-1-dev libtelnet-dev"
    result=$( apt-get install -y libfreerdp-dev libpango1.0-dev libssh2-1-dev libtelnet-dev)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software for guacamole, pls install guacamole manually"
        exit
    fi
    echo "installing libvncserver-dev libpulse-dev libwebp-dev libssl-dev libvorbis-dev"
    result=$( apt-get install -y libvncserver-dev libpulse-dev libwebp-dev libssl-dev libvorbis-dev)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software for guacamole, pls install guacamole manually"
        exit
    fi
}

install_and_config_guacamole() {
    result=$(sudo service guacd restart)
    if grep -q "SUCCESS" <<< $result; then
        echo "guacamole is installed!"
        return
    fi
    # install and Configure guacamole
    cd /home/opentech &&  wget http://sourceforge.net/projects/guacamole/files/current/source/guacamole-server-0.9.9.tar.gz/download
    rm -rf guacamole-server-0.9.9
    mv download guacamole-server-0.9.9.tar.gz &&  tar -xzf guacamole-server-0.9.9.tar.gz && cd guacamole-server-0.9.9/
    $(autoreconf -fi)
    $(./configure --with-init-dir=/etc/init.d)
    $(make)
    $(make install)
    ldconfig
    # configure guacamole client
    wget http://sourceforge.net/projects/guacamole/files/current/binary/guacamole-0.9.9.war/download
    mv download /var/lib/tomcat7/webapps/guacamole.war
    # configure guacamole authentication provider
    mkdir /usr/share/tomcat7/.guacamole
    mkdir /etc/guacamole
    cd /home/opentech/open-hackathon/deploy/guacamole
    cp guacamole-sample.properties /etc/guacamole/guacamole.properties
    cp *.jar /etc/guacamole
    ln -s /etc/guacamole/guacamole.properties /usr/share/tomcat7/.guacamole/guacamole.properties
    result=$(sudo service guacd restart)
    if ! (grep -q "SUCCESS" <<< $result); then
        echo "Fail to install guacamole, please run this script once again!"
        exit
    fi
}


# install docker
install_and_config_docker() {
    result=$( apt-get update)
    if grep -q "Could not resolve" <<< $result; then
        echo "Could not update apt-get, please solve it"
        exit
    fi
    result=$( apt-get install apt-transport-https ca-certificates)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software for docker, pls install docker manually"
        exit
    fi

    result=$( apt-get update)
    if grep -q "Could not resolve" <<< $result; then
        echo "Could not update apt-get, please solve it"
        exit
    fi
    result=$( apt-get purge lxc-docker)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install docker, pls install docker manually"
    fi
    $(apt-cache policy docker-engine)
    # for ubuntu 15
    result=$(apt-get install -y linux-image-extra-$(uname -r))
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install linux-image-extra-$(uname -r)"
        exit
    fi
    # for ubuntu 12 & 14
    result=$(apt-get install -y apparmor)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install apparmor"
        exit
    fi
    result=$(apt-get install -y docker-engine)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install apparmor"
        exit
    fi
    service docker start
    
    result=$(docker run hello-world)
    if grep -q "Hello from Docker" <<< $result; then
        echo "Install docker failed, please run this script again"
    fi

    usermod -aG docker ubuntu

    groupadd docker
    gpasswd -a ${USER} docker

    docker pull rastasheep/ubuntu-sshd
}


deploy() {
    # Logging && Hosts
    mkdir /var/log/open-hackathon
    chmod -R 644 /var/log/open-hackathon

    if grep -qs "open-hackathon-dev.chinacloudapp.cn" /etc/hosts; then
        echo "127.0.0.1 open-hackathon-dev.chinacloudapp.cn" >> /etc/hosts
    fi

    # Installing uWSGI
    $(pip install uwsgi)
    cp /home/opentech/open-hackathon/open-hackathon-server/src/open-hackathon-server.conf /etc/init/
    cp /home/opentech/open-hackathon/open-hackathon-client/src/open-hackathon-client.conf /etc/init/
}

echo "It may take a long time to install and configure open-hackathon, please wait a moment^_^, ..."
echo "安装将花费一定时间，请耐心等待直到安装完成^_^, ..."

get_dependency_software
set_envirement
get_dependency_for_guacamole
install_and_config_guacamole
install_and_config_docker
deploy



