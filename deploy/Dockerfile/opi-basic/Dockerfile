FROM ubuntu:latest
MAINTAINER Ice Shi 
ENV DEBIAN_FRONTEND noninteractive

# need install git, vim, openssh-server, 

RUN apt-get update

RUN apt-get install -y --force-yes git vim o

RUN apt-get install -y openssh-server && \
    mkdir -p /var/run/sshd && \
    echo 'root:acoman' |chpasswd
    sed -i "s/PermitRootLogin without-password/#PermitRootLogin yes/" /etc/ssh/sshd_config
    echo "ClientAliveInterval 120" >> /etc/ssh/sshd_config

EXPOSE 22

CMD ["/usr/sbin/sshd","-D"]