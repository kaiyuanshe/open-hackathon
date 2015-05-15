FROM ubuntu:14.04
ENV DEBIAN_FRONTEND noninteractive
MAINTAINER Ice Shi 

ENV CHEF_CLIENT_VER 12.2.1-1
#install chef-client
#RUN cd /tmp && wget -q -H 
ADD chef_${CHEF_CLIENT_VER}_amd64.deb /tmp/chef_${CHEF_CLIENT_VER}_amd64.deb
RUN cd /tmp && \
    dpkg -i chef_${CHEF_CLIENT_VER}_amd64.deb
 
# install SSH
RUN apt-get update && \
    apt-get install openssh-server -y && \
    mkdir /var/run/sshd && \
    echo 'root:acoman' | chpasswd && \
    sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config

#add chef-repo files to docker
ADD chef-repo /tmp/chef-repo
RUN cd /tmp/chef-repo && knife bootstrap localhost -p 22 -x 'root' -P 'acoman' -N 'testnode' -r 'test




#Add SSH client keep alive support
RUN sed -i 's/ClientAliveInterval 120' /etc/ssh/sshd_config

EXPOSE 22

CMD ["/usr/sbin/sshd","-D"]
