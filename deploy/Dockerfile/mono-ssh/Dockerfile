# -*- coding: utf-8 -*-
#
# This file is covered by the LICENSING file in the root of this project.
#

# docker file for ssh
FROM msopentechcn/mono

RUN apt-get install openssh-server -y
RUN mkdir /var/run/sshd
RUN echo 'root:acoman' | chpasswd
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config


EXPOSE 22

CMD ["/usr/sbin/sshd","-D"]