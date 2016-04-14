FROM rastasheep/ubuntu-sshd:latest

MAINTAINER Junbo Wang

# Config SSH
RUN sed -i 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config
RUN sed -i '$a\ClientAliveInterval 120' /etc/ssh/sshd_config
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config

EXPOSE 22
EXPOSE 80

CMD    ["/usr/sbin/sshd", "-D"]