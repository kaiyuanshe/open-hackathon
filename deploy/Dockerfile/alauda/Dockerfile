# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------

FROM ubuntu:14.04
ENV DEBIAN_FRONTEND noninteractive
MAINTAINER Microsoft Open Technologies (Shanghai) Co. Ltd.

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