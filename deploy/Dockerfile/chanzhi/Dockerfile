# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Asia-Pacific R&D Group. All rights reserved.
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

MAINTAINER Microsoft Asia-Pacific R&D Group

#
# Config SSH
#
RUN apt-get update
RUN apt-get install -y openssh-server sudo

RUN sed -i 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config
RUN sed -i '$a\ClientAliveInterval 120' /etc/ssh/sshd_config
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config

RUN useradd admin
RUN echo "admin:admintest" | chpasswd
RUN echo "admin   ALL=(ALL)       ALL" >> /etc/sudoers
RUN echo "root:roottest" | chpasswd

RUN mkdir /var/run/sshd
EXPOSE 22

#
# Config Mysql
#
RUN apt-get install mysql-server libmysqlclient-dev -y

RUN /usr/sbin/mysqld  & \
        sleep 10s &&\
        mysql -e "grant all privileges on *.* to 'root'@'%' identified by 'roottest';"&&\
    mysql -e "grant all privileges on *.* to 'root'@'localhost' identified by 'roottest';"&&\
    mysql -u root -proottest -e "show databases;"
RUN sed -i 's/bind-address/#bind-address/g' /etc/mysql/my.cnf

#EXPOSE 3306

#
# Config Apache and PHP
#
RUN apt-get install apache2 -y
RUN apt-get install php5 php5-mysql -y
RUN apt-get install zip -y

RUN wget -P /opt http://dl.cnezsoft.com/chanzhi/5.1/chanzhiEPS.5.1.zip
RUN unzip /opt/chanzhiEPS.5.1.zip -d /opt
RUN cp -r /opt/chanzhieps/www  /var/
RUN cp -r /opt/chanzhieps/www/* /var/www/html
RUN cp -r /opt/chanzhieps/system /var/www

RUN chmod o=rwx -R /var/www/system/tmp
RUN chmod o=rwx -R /var/www/html/data
RUN chown -R www-data:www-data /var/www

EXPOSE 80

#
# Config Chanzhi
#

RUN sed -i "s/'dbHost', '127.0.0.1'/'dbHost', '127.0.0.1'/g" /var/www/system/module/install/view/step2.html.php
RUN sed -i "s/'dbPort', '3306'/'dbPort', '3306', 'readonly'/g" /var/www/system/module/install/view/step2.html.php
RUN sed -i "s/'dbUser', ''/'dbUser', 'root', 'readonly'/g" /var/www/system/module/install/view/step2.html.php
RUN sed -i "s/'dbPassword', ''/'dbPassword', 'roottest', 'readonly'/g" /var/www/system/module/install/view/step2.html.php
RUN sed -i "s/'dbName', ''/'dbName', 'chanzhi'/g" /var/www/system/module/install/view/step2.html.php
RUN rm /var/www/html/index.html

#
# Build run.sh
#
RUN touch /run.sh
RUN echo '#!/bin/sh' >> /run.sh
RUN echo 'service mysql restart' >> /run.sh
RUN echo '(mysqld &)' >> /run.sh
RUN echo '/usr/sbin/apache2ctl start' >> /run.sh
RUN echo '/usr/sbin/sshd -D' >> /run.sh

CMD ["/bin/sh", "/run.sh"]
