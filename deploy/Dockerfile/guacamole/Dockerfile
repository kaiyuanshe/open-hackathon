# -*- coding: utf-8 -*-
#
# This file is covered by the LICENSING file in the root of this project.
#

### Dockerfile for guacamole
### Includes all the optional authentication modules preinstalled

FROM phusion/baseimage:0.9.15
### based on Randy hall's hall/guacamole
MAINTAINER Ice Shi 
CMD ["/sbin/my_init"]
ENV HOME /root
ENV DEBIAN_FRONTEND noninteractive

### Don't let apt install docs or man pages
#   ADD excludes /etc/dpkg/dpkg.cfg.d/excludes

### Update system
RUN apt-get update 
### Install packages and clean up in one command to reduce build size

RUN apt-get install -y --no-install-recommends libcairo2-dev libpng12-dev freerdp-x11 libssh2-1 \
    libfreerdp-dev libvorbis-dev libssl0.9.8 gcc libssh-dev libpulse-dev tomcat7 tomcat7-admin \
    libpango1.0-dev libssh2-1-dev autoconf wget libossp-uuid-dev libtelnet-dev libvncserver-dev \
    build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
                            /usr/share/man /usr/share/groff /usr/share/info \
                            /usr/share/lintian /usr/share/linda /var/cache/man && \
    (( find /usr/share/doc -depth -type f ! -name copyright|xargs rm || true )) && \
    (( find /usr/share/doc -empty|xargs rmdir || true )) 

### Install the authentication extensions in the classpath folder
### and the client app in the tomcat webapp folder
### Version of guacamole to be installed
ENV GUAC_VER 0.9.6
### Version of mysql-connector-java to install
ENV MCJ_VER 5.1.35
### config directory and classpath directory
run mkdir -p /etc/guacamole /var/lib/guacamole/classpath 

### Install LDAP Authentication extension
RUN cd /tmp && \
    wget -q --span-hosts http://downloads.sourceforge.net/project/guacamole/current/extensions/guacamole-auth-ldap-${GUAC_VER}.tar.gz && \
    tar -zxf guacamole-auth-ldap-$GUAC_VER.tar.gz && \
    mv -f `find . -type f -name '*.jar'` /var/lib/guacamole/classpath && \
    rm -Rf /tmp/*

### Install NOAUTH Authentication extension
RUN cd /tmp && \
    wget -q --span-hosts http://downloads.sourceforge.net/project/guacamole/current/extensions/guacamole-auth-noauth-${GUAC_VER}.tar.gz && \
    tar -zxf guacamole-auth-noauth-$GUAC_VER.tar.gz && \
    mv -f `find . -type f -name '*.jar'` /var/lib/guacamole/classpath && \
    rm -Rf /tmp/*

### Install MySQL Authentication Module
RUN cd /tmp && \
    wget -q --span-hosts http://downloads.sourceforge.net/project/guacamole/current/extensions/guacamole-auth-mysql-${GUAC_VER}.tar.gz && \
    tar -zxf guacamole-auth-mysql-$GUAC_VER.tar.gz && \
    mv -f `find . -type f -name '*.jar'` /var/lib/guacamole/classpath && \
    mv -f guacamole-auth-mysql-$GUAC_VER/schema/*.sql /root &&\
    rm -Rf /tmp/*

### Install dependancies for mysql authentication module
RUN cd /tmp && \
    wget -q --span-hosts http://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-${MCJ_VER}.tar.gz && \
    tar -zxf mysql-connector-java-$MCJ_VER.tar.gz && \
    mv -f `find . -type f -name '*.jar'` /var/lib/guacamole/classpath && \
    rm -Rf /tmp/*

### Install precompiled client webapp
RUN cd /var/lib/tomcat7/webapps && \
    rm -Rf ROOT && \
    wget -q --span-hosts http://sourceforge.net/projects/guacamole/files/current/binary/guacamole-${GUAC_VER}.war && \
    ln -s guacamole-$GUAC_VER.war ROOT.war && \
    ln -s guacamole-$GUAC_VER.war guacamole.war 

### Compile and install guacamole server
RUN cd /tmp && \
    wget -q --span-hosts http://sourceforge.net/projects/guacamole/files/current/source/guacamole-server-${GUAC_VER}.tar.gz && \
    tar -zxf guacamole-server-$GUAC_VER.tar.gz && \
    cd guacamole-server-$GUAC_VER && \
    ./configure --with-init-dir=/etc/init.d && \
    make && \ 
    make install && \
    update-rc.d guacd defaults && \
    ldconfig && \
    cd /usr/share/tomcat7 && \
    ln -s /etc/guacamole .guacamole && \
    rm -Rf /tmp/*

### Install HMAC Authentication module
#   Installed as precompiled jar so the container doesn't get bloated
#
#   get clone https://github.com/grncdr/guacamole-auth-hmac.git
#   cd guacamole-auth-hmac
#   mvn package
#   cp target/guacamole-auth-hmac-1.0-SNAPSHOT.jar /var/lib/tomcat7/webapps
### ADD guacamole-auth-hmac-1.0-SNAPSHOT.jar /var/lib/guacamole/classpath/guacamole-auth-hmac-1.0-SNAPSHOT.jar

### Configure Service Startup
ADD rc.local /etc/rc.local
RUN chmod a+x /etc/rc.local

### Disable SSH in the container
#   rm -rf /etc/service/sshd /etc/my_init.d/00_regen_ssh_host_keys.sh

### END
### To make this a functional guacamole container, you must map /etc/guacamole of this container
### To a folder on your host machine.  You can also build a new container based on this one
### adding your config files directly inside your new container.  See the sampleconfigs directory
### for examples.
###
### This container is used as a base for
### hall/guacamole-guacd - Runs only the guqcd daemon and exports the ports to other containers
### hall/guacamole-mysql - Links to hall/quacamole-guacd, stackbrew/mysql and stores the config
###                        database in a persistent container.