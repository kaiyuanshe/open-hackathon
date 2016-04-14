#!/bin/bash
:<<BLOCK
Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.

The MIT License (MIT)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
BLOCK


# This script should be run as "sudo bash setup.sh"
# Better to deploy open-hackathon on ubuntu 14


function pre_setup_docker() {
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

function get_dependency_software() {
    echo "updating apt-get......"
    result=$(apt-get update)
    if grep -q "Could not resolve" <<< $result; then
        echo "Could not update apt-get, please solve it"
        exit
    fi
    echo "installing git python-setuptools python-dev python-pip"
    result=$(apt-get install -y git python-setuptools python-dev python-pip)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software, pls install docker manually"
        exit
    fi
    echo "installing autoconf libtool tomcat7 "
    result=$(apt-get install -y autoconf automake libtool tomcat7 )
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software, pls install docker manually"
        exit
    fi
}

function set_envirement() {
    echo "git clone source code from Github, and solve python dependency"
    if [ ! -d $HOME ]; then
        mkdir $HOME
    fi
    cd $HOME
    if [ ! -d "$OHP_HOME" ]; then
        echo "git cloning open-hackathon source code"
        result=$(git clone https://github.com/msopentechcn/open-hackathon.git)
        if grep -q "unable to access" <<< $result; then
            echo "Could not git clone open-hackathon source code, pls check your network"
            exit
        fi
    fi

    cd $OHP_HOME
    git reset --hard
    git pull
    echo "pip is installing required python library"
    result=$(pip install -r open-hackathon-server/requirement.txt)

    result=$(pip install -r open-hackathon-client/requirement.txt)
    cp open-hackathon-server/src/hackathon/config_sample.py open-hackathon-server/src/hackathon/config.py
    cp open-hackathon-server/src/hackathon/config_sample.py open-hackathon-server/src/hackathon/config.py
}

function install_mongodb() {
   result=$(sudo service mongod status)
   if $(grep -q "mongod" <<< $result); then
       echo "mongodb is installed"
       return
   fi
   apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927

   if $(lsb_release -d | grep -q "12"); then
        echo "deb http://repo.mongodb.org/apt/ubuntu precise/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
   fi
   if $(lsb_release -d | grep -q "14"); then
        echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
   fi
   if $(lsb_release -d | grep -q "Mint"); then
        echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
   fi
   result=$(apt-get update)
   echo "installing mongodb-org"
   result=$(apt-get install -y mongodb-org)
   echo "installing mongodb-org=$MONGO_VERSION mongodb-org-server=$MONGO_VERSION mongodb-org-shell=$MONGO_VERSION mongodb-org-mongos=$MONGO_VERSION mongodb-org-tools=$MONGO_VERSION"
   result=$(apt-get install -y mongodb-org=$MONGO_VERSION mongodb-org-server=$MONGO_VERSION mongodb-org-shell=$MONGO_VERSION mongodb-org-mongos=$MONGO_VERSION mongodb-org-tools=$MONGO_VERSION)
   if grep -q "Unable to lacate" <<< $result; then
       echo "Could not install mongodb, pls run this script again or install mongodb manually"
       exit
   fi
   echo "mongodb-org hold" | sudo dpkg --set-selections
   echo "mongodb-org-server hold" | sudo dpkg --set-selections
   echo "mongodb-org-shell hold" | sudo dpkg --set-selections
   echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
   echo "mongodb-org-tools hold" | sudo dpkg --set-selections
   service mongod start
   cd $OHP_HOME && python open-hackathon-server/src/setup_db.py
}

function get_dependency_for_guacamole() {
    echo "solve dependency software for guacamole"
    result=$(service guacd restart)
    if grep -q "SUCCESS" <<< $result; then
        echo "guacamole is installed!"
        return
    fi
    echo "installing libcairo2-dev"
    result=$(apt-get install -y libcairo2-dev)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software for guacamole, pls install guacamole manually"
        exit
    fi
    echo "installing libjpeg62-dev libpng12-dev libossp-uuid-dev"
    result=$(apt-get install -y libjpeg62-dev libpng12-dev libossp-uuid-dev)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software for guacamole, pls install guacamole manually"
        exit
    fi
    echo "installing libfreerdp-dev libpango1.0-dev libssh2-1-dev libtelnet-dev"
    result=$(apt-get install -y libfreerdp-dev libpango1.0-dev libssh2-1-dev libtelnet-dev)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software for guacamole, pls install guacamole manually"
        exit
    fi
    echo "installing libvncserver-dev libpulse-dev libwebp-dev libssl-dev libvorbis-dev"
    result=$(apt-get install -y libvncserver-dev libpulse-dev libwebp-dev libssl-dev libvorbis-dev)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software for guacamole, pls install guacamole manually"
        exit
    fi
}

function install_and_config_guacamole() {
    result=$(service guacd restart)
    if grep -q "SUCCESS" <<< $result; then
        echo "guacamole is installed!"
        return
    fi
    echo "installing guacamole"
    # install and Configure guacamole
    cd $OHP_HOME
    if [ ! -d "guacamole-server-$GUACAMOLE_VERSION" ]; then
        wget http://sourceforge.net/projects/guacamole/files/current/source/guacamole-server-$GUACAMOLE_VERSION.tar.gz/download
        mv download guacamole-server-$GUACAMOLE_VERSION.tar.gz &&  tar -xzf guacamole-server-$GUACAMOLE_VERSION.tar.gz
    fi
    cd guacamole-server-$GUACAMOLE_VERSION
    result=$(autoreconf -fi)
    result=$(./configure --with-init-dir=/etc/init.d)
    result=$(make clean)
    result=$(make)
    result=$(make install)
    ldconfig
    # configure guacamole client
    if [ ! -f /var/lib/tomcat7/webapps/guacamole.war ] ; then
        wget http://sourceforge.net/projects/guacamole/files/current/binary/guacamole-$GUACAMOLE_VERSION.war/download
        mv download /var/lib/tomcat7/webapps/guacamole.war
    fi
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
    result=$(service tomcat7 restart)
    echo "guacamole installed successfully"
}


function install_and_config_docker() {
    # install docker
    result=$(apt-get update)
    if grep -q "Could not resolve" <<< $result; then
        echo "Could not update apt-get, please solve it"
        exit
    fi
    result=$(apt-get install apt-transport-https ca-certificates)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install dependancy software for docker, pls install docker manually"
        exit
    fi

    result=$(apt-get update)
    if grep -q "Could not resolve" <<< $result; then
        echo "Could not update apt-get, please solve it"
        exit
    fi
    result=$(apt-get purge lxc-docker)
    if grep -q "Unable to lacate" <<< $result; then
        echo "Could not install docker, pls install docker manually"
        exit
    fi
    result=$(apt-cache policy docker-engine)
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

    echo "docker installed successfully"

    usermod -aG docker ubuntu

    groupadd docker
    gpasswd -a ${USER} docker

    docker pull rastasheep/ubuntu-sshd
    result=$(docker run hello-world)
    if ! (grep -q "Hello from Docker" <<< $result); then
        echo "Install docker failed, please run this script again or install docker manually."
        exit
    fi
    echo "Docker is installed successfully."
}


function deploy() {
    # Logging && Hosts
    result=$(mkdir /var/log/open-hackathon)
    chmod -R 644 /var/log/open-hackathon

    # Installing uWSGI
    result=$(pip install uwsgi)
    cp $OHP_HOME/open-hackathon-server/src/open-hackathon-server.conf /etc/init/
    cp $OHP_HOME/open-hackathon-client/src/open-hackathon-client.conf /etc/init/
}


function main() {
    if [ $(id -u) != "0" ]; then
        echo "Please run this script with sudo"
        echo "like sudo bash setup.sh"
        exit 1
    fi
    export HOME=/home/opentech
    export OHP_HOME=$HOME/open-hackathon
    export MONGO_VERSION=3.2.4
    export GUACAMOLE_VERSION=0.9.9
    echo "It may take a long time to install and configure open-hackathon, please wait a moment^_^, ..."
    echo "安装将花费一定时间，请耐心等待直到安装完成^_^, ..."
    get_dependency_software
    install_mongodb
    set_envirement
    get_dependency_for_guacamole
    install_and_config_guacamole
    #pre_setup_docker
    #install_and_config_docker
    deploy
    chown -R $(logname) $HOME
}

main