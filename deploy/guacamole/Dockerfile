# -*- coding: utf-8 -*-
#
# This file is covered by the LICENSING file in the root of this project.
#

### Dockerfile for guacamole
### based on guacamole official image

FROM guacamole/guacamole:0.9.14

ENV GUACAMOLE_HOME /etc/guacamole

RUN mkdir -p /usr/local/tomcat/.guacamole
RUN mkdir -p /etc/guacamole/extensions
COPY guacamole-sample.properties /etc/guacamole/guacamole.properties
COPY *.jar /etc/guacamole/extensions/
RUN ln -s /etc/guacamole/guacamole.properties /usr/local/tomcat/.guacamole/guacamole.properties

