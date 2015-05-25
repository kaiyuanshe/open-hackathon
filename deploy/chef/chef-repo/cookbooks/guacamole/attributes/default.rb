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
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

default['guacamole']['version'] = '0.9.6'
default['guacamole']['dir'] = '/opt/gua-dir'
default['guacamole']['server-tar'] = "guacamole-server-#{node['guacamole']['version']}.tar.gz"
default['guacamole']['server-tar-url'] = "http://jaist.dl.sourceforge.net/project/guacamole/current/source/guacamole-server-#{node['guacamole']['version']}.tar.gz"
default['guacamole']['client-tar'] = "guacamole-client-#{node['guacamole']['version']}.tar.gz"
default['guacamole']['server-tar-extract-dir'] = "#{node['guacamole']['dir']}/extract"
default['guacamole']['war-path'] = "#{node['tomcat']['webapp_dir']}/guacamole.war"
default['guacamole']['war-url'] = "http://jaist.dl.sourceforge.net/project/guacamole/current/binary/guacamole-#{node['guacamole']['version']}.war"
default['guacamole']['war-cookbook-file'] = "guacamole-#{node['guacamole']['version']}.war"
default['guacamole']['use-local-war'] = 'true'

default['guacamole']['src-folder'] = "#{node['openhackathon'][:base_dir]}/deploy/guacamole"

default['guacamole']['tomcat-guacamole-share-folder'] = "#{node['tomcat']['base']}/.guacamole"

default['guacamole']['properties'] = 'guacamole.properties'
default['guacamole']['json-jar'] = 'json-20090211.jar'
default['guacamole']['provider-jar'] = 'openhackathon-gucamole-authentication-1.0-SNAPSHOT.jar'

default['guacamole']['guacd-hostname'] = 'localhost'
default['guacamole']['guacd-port'] = '4822'
default['guacamole']['lib-directory'] = '/etc/guacamole'
default['guacamole']['auth-provider'] = 'com.openhackathon.guacamole.OpenHackathonAuthenticationProvider'
default['guacamole']['auth-request-url'] = '/api/guacamoleconfig'


