#!/bin/bash
pre_setup() {
    #for ubuntu 14
    if $(lsb_release -d | grep -q "14"); then
        echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" | tee /etc/apt/sources.list.d/docker.list
    fi

    # for ubuntu 15
    if $(lsb_release -d | grep -q "15"); then
        echo "deb https://apt.dockerproject.org/repo ubuntu-wily main" | tee /etc/apt/sources.list.d/docker.list
    fi

    # for linux mint
    if $(lsb_release -d | grep -q "Mint"); then
        echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" | tee /etc/apt/sources.list.d/docker.list
    fi

    apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
}

get_dependency_software() {
    echo "updating apt-get......"
    result=$(sudo apt-get update)
    if grep -q "Could not resolve" <<< $result; then
        echo "Could not update apt-get, please solve it"
        exit
    fi
    echo "installing git python-setuptools python-dev python-pip"
    result=$(sudo apt-get install -y git python-setuptools python-dev python-pip)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software, pls install docker manually"
        exit
    fi
    echo "installing autoconf libtool tomcat7 "
    result=$(sudo apt-get install -y autoconf automake libtool tomcat7 )
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software, pls install docker manually"
        exit
    fi
}

set_envirement() {
    echo "git clone source code from Github, and solve python dependency"
    cd /home &&  rm -rf opentech
    mkdir opentech && cd opentech
    rm -r open-hackathon
    echo "git cloning open-hackathon source code"
    result=$(sudo git clone https://github.com/YaningX/open-hackathon.git)
    if grep -q "unable to access" <<< $result; then
        echo "Could not git clone open-hackathon source code, pls check your network"
        exit
    fi
    cd /home/opentech/open-hackathon
    echo "pip is installing required python library"
    result=$(sudo pip install -r open-hackathon-server/requirement.txt)

    result=$(sudo pip install -r open-hackathon-client/requirement.txt)
    cp open-hackathon-server/src/hackathon/config_sample.py open-hackathon-server/src/hackathon/config.py
    cp open-hackathon-server/src/hackathon/config_sample.py open-hackathon-server/src/hackathon/config.py
}

install_mongodb() {
   result=$(sudo service mongod status)
   if ! $(grep "unrecognized service" <<< $result); then
       echo "mongodb is installed"
       return
   fi
   sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
   if $(lsb_release -d | grep -q "14"); then
        echo "deb http://repo.mongodb.com/apt/ubuntu trusty/mongodb-enterprise/3.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-enterprise.list
   fi
   if $(lsb_release -d | grep -q "Mint"); then
        echo "deb http://repo.mongodb.com/apt/ubuntu trusty/mongodb-enterprise/3.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-enterprise.list
   fi
   if $(lsb_release -d | grep -q "Mint"); then
        echo "deb http://repo.mongodb.com/apt/ubuntu precise/mongodb-enterprise/3.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-enterprise.list
   fi
   echo "deb http://repo.mongodb.com/apt/ubuntu "$(lsb_release -sc)"/mongodb-enterprise/2.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-enterprise-2.6.list
   result=$(sudo apt-get update)
   echo "installing mongodb-enterprise"
   result=$(sudo apt-get install -y mongodb-enterprise)
   echo "installing mongodb-enterprise=3.0.11 mongodb-enterprise-server=3.0.11 mongodb-enterprise-shell=3.0.11 mongodb-enterprise-mongos=3.0.11 mongodb-enterprise-tools=3.0.11"
   result=$(sudo apt-get install -y mongodb-enterprise=3.0.11 mongodb-enterprise-server=3.0.11 mongodb-enterprise-shell=3.0.11 mongodb-enterprise-mongos=3.0.11 mongodb-enterprise-tools=3.0.11)
   if grep -q "Unable to lacate" <<< $result; then
       echo "Could not install mongodb, pls run this script again or install mongodb manually"
       exit
   fi
   echo "mongodb-enterprise hold" | sudo dpkg --set-selections
   echo "mongodb-enterprise-server hold" | sudo dpkg --set-selections
   echo "mongodb-enterprise-shell hold" | sudo dpkg --set-selections
   echo "mongodb-enterprise-mongos hold" | sudo dpkg --set-selections
   echo "mongodb-enterprise-tools hold" | sudo dpkg --set-selections
   service mongod start
   cd /home/opentech/ && python open-hackathon-server/src/setup_db.py
}

get_dependency_for_guacamole() {
    echo "solve dependency software for guacamole"
    result=$(sudo service guacd restart)
    if grep -q "SUCCESS" <<< $result; then
        echo "guacamole is installed!"
        return
    fi
    echo "installing libcairo2-dev"
    result=$(sudo apt-get install -y libcairo2-dev)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software for guacamole, pls install guacamole manually"
        exit
    fi
    echo "installing libjpeg62-dev libpng12-dev libossp-uuid-dev"
    result=$(sudo apt-get install -y libjpeg62-dev libpng12-dev libossp-uuid-dev)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software for guacamole, pls install guacamole manually"
        exit
    fi
    echo "installing libfreerdp-dev libpango1.0-dev libssh2-1-dev libtelnet-dev"
    result=$(sudo apt-get install -y libfreerdp-dev libpango1.0-dev libssh2-1-dev libtelnet-dev)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software for guacamole, pls install guacamole manually"
        exit
    fi
    echo "installing libvncserver-dev libpulse-dev libwebp-dev libssl-dev libvorbis-dev"
    result=$(sudo apt-get install -y libvncserver-dev libpulse-dev libwebp-dev libssl-dev libvorbis-dev)
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
    echo "install guacamole"
    # install and Configure guacamole
    cd /home/opentech &&  wget http://sourceforge.net/projects/guacamole/files/current/source/guacamole-server-0.9.9.tar.gz/download
    rm -rf guacamole-server-0.9.9
    mv download guacamole-server-0.9.9.tar.gz &&  tar -xzf guacamole-server-0.9.9.tar.gz && cd guacamole-server-0.9.9/
    result=$(autoreconf -fi)
    result=$(./configure --with-init-dir=/etc/init.d)
    result=$(make)
    result=$(make install)
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
    echo "guacamole installed successfully"
}


install_and_config_docker() {
    # install docker
    result=$(sudo apt-get update)
    if grep -q "Could not resolve" <<< $result; then
        echo "Could not update apt-get, please solve it"
        exit
    fi
    result=$(sudo apt-get install apt-transport-https ca-certificates)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software for docker, pls install docker manually"
        exit
    fi

    result=$(sudo apt-get update)
    if grep -q "Could not resolve" <<< $result; then
        echo "Could not update apt-get, please solve it"
        exit
    fi
    result=$(sudo apt-get purge lxc-docker)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install docker, pls install docker manually"
        exit
    fi
    result=$(sudo apt-cache policy docker-engine)
    # for ubuntu 15
    result=$(sudo apt-get install -y linux-image-extra-$(uname -r))
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install linux-image-extra-$(uname -r)"
        exit
    fi
    # for ubuntu 12 & 14
    result=$(sudo apt-get install -y apparmor)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install apparmor"
        exit
    fi
    result=$(sudo apt-get install -y docker-engine)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install apparmor"
        exit
    fi
    service docker start

    echo "docker installed successfully"

    usermod -aG docker ubuntu

    groupadd docker
    gpasswd -a ${USER} docker

    docker pull rastasheep/ubuntu-sshd
    result=$(sudo docker run hello-world)
    if ! (grep -q "Hello from Docker" <<< $result); then
        echo "Install docker failed, please run this script again"
        exit
    fi
}


deploy() {
    # Logging && Hosts
    mkdir /var/log/open-hackathon
    chmod -R 644 /var/log/open-hackathon

    if ! $(grep -qs "open-hackathon-dev.chinacloudapp.cn" /etc/hosts); then
        echo "127.0.0.1 open-hackathon-dev.chinacloudapp.cn" >> /etc/hosts
    fi

    # Installing uWSGI
    result=$(pip install uwsgi)
    cp /home/opentech/open-hackathon/open-hackathon-server/src/open-hackathon-server.conf /etc/init/
    cp /home/opentech/open-hackathon/open-hackathon-client/src/open-hackathon-client.conf /etc/init/
}





main() {
    echo "It may take a long time to install and configure open-hackathon, please wait a moment^_^, ..."
    echo "安装将花费一定时间，请耐心等待直到安装完成^_^, ..."

    pre_setup
    get_dependency_software
    install_mongodb
    set_envirement
    get_dependency_for_guacamole
    install_and_config_guacamole
    install_and_config_docker
    deploy
}

main



