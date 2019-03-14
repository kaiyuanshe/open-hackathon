# -*- coding: utf-8 -*-
#
# This file is covered by the LICENSING file in the root of this project.
#

FROM ubuntu:14.04
ENV DEBIAN_FRONTEND noninteractive
MAINTAINER Kaiyuanshe

ENV CHEF_CLIENT_VER 12.2.1-1

#git source code
RUN cd /opt/ && \
    git clone https://github.com/msopentechcn/open-hackathon.git

#change apt source list
#COPY sources.list /tmp/sources.list
RUN cat /opt/open-hackathon/deploy/Dockerfile/hackathon-docker/sources.list >> /etc/apt/sources.list

# Install basic tools
RUN apt-get update && \
    apt-get install -y git vim

# Install chef-client
#RUN cd /tmp && wget -q -H     && \

#ADD chef_${CHEF_CLIENT_VER}_amd64.deb /tmp/chef_${CHEF_CLIENT_VER}_amd64.deb
RUN cd /opt/open-hackathon/deploy/Dockerfile/hackathon-docker && dpkg -i chef_${CHEF_CLIENT_VER}_amd64.deb

# Config SSH
RUN  apt-get install openssh-server -y && \
     mkdir /var/run/sshd && \
     echo 'root:acoman' | chpasswd && \
     sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
     echo 'ClientAliveInterval 120' >> /etc/ssh/sshd_config


# Add chef-repo files to docker
RUN mkdir /etc/chef && \
    cp -r /opt/open-hackathon/deploy/Dockerfile/hackathon-docker/* /etc/chef
    cd /etc/chef && \
    chef-client -r 'role[hackathon-docker]' --environment hackathon-docker

# Install supervisor
RUN  apt-get install supervisor -y

COPY services.conf /etc/supervisor/conf.d/services.conf
#RUN touch /etc/supervisor/conf.d/services.conf && \
#    echo "[program:tomcat]" >> /etc/supervisor/conf.d/services.conf && \
#    echo "command= service tomcat7 start" >> /etc/supervisor/conf.d/services.conf && \
#    echo "redirect_stderr=true" >> /etc/supervisor/conf.d/services.conf

EXPOSE 22 80 8000 8080 15000


CMD ["supervisord", "-c", "/etc/supervisor.conf"]