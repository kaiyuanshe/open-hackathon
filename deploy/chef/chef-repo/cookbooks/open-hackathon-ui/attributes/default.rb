# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
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

default['open-hackathon-ui']['HOSTNAME'] = 'http://open-hackathon-dev.chinacloudapp.cn'
default['open-hackathon-ui']['QQ_OAUTH_STATE'] = 'openhackathon'
default['open-hackathon-ui']['HACKATHON_API_ENDPOINT'] = 'http://open-hackathon.chinacloudapp.cn:15002'
default['open-hackathon-ui']['environment'] = 'local'

default['open-hackathon-ui']['github']['client_id'] = 'a10e2290ed907918d5ab' 
default['open-hackathon-ui']['github']['client_secret'] = '5b240a2a1bed6a6cf806fc2f34eb38a33ce03d75'
default['open-hackathon-ui']['github']['scope'] = 'user'

default['open-hackathon-ui']['qq']['client_id'] = '101192358'
default['open-hackathon-ui']['qq']['client_secret'] = 'd94f8e7baee4f03371f52d21c4400cab'
default['open-hackathon-ui']['qq']['scope'] = 'get_user_info'
default['open-hackathon-ui']['qq']['response_type'] = 'code'
default['open-hackathon-ui']['qq']['grant_type'] = 'authorization_code'
default['open-hackathon-ui']['qq']['meta_content'] = '274307566465013314076545663016134754100636'

default['open-hackathon-ui']['gitcafe']['client_id'] = '25ba4f6f90603bd2f3d310d11c0665d937db8971c8a5db00f6c9b9852547d6b8'
default['open-hackathon-ui']['gitcafe']['client_secret'] = 'e3d821e82d15096054abbc7fbf41727d3650cab6404a242373f5c446c0918634'
default['open-hackathon-ui']['gitcafe']['response_type'] = 'code'
default['open-hackathon-ui']['gitcafe']['scope'] = 'public'
default['open-hackathon-ui']['gitcafe']['grant_type'] = 'authorization_code'

default['open-hackathon-ui']['hackathon']['name'] = 'open-xml-sdk'

default['open-hackathon-ui']['provider'] ='["github","qq","gitcafe","weibo"]'
default['open-hackathon-ui']['session_minutes'] = '60'
default['open-hackathon-ui']['token_expiration_minutes'] = '60*24'

default['open-hackathon-ui']['weibo']['meta_content'] = 'a6a3b875cfdf95e2'
default['open-hackathon-ui']['weibo']['client_id'] = '582725653'
default['open-hackathon-ui']['weibo']['client_secret'] = '28f5325cb57613b9f135185b5245c5a2'
default['open-hackathon-ui']['weibo']['grant_type'] = 'authorization_code'
default['open-hackathon-ui']['weibo']['scope'] = 'all'

default['open-hackathon-ui']['git']['repository'] = 'https://github.com/msopentechcn/open-hackathon.git'
default['open-hackathon-ui']['git']['revision'] = 'master'

default['open-hackathon-ui']['global-user'] = 'openhackathon'

default['open-hackathon-ui']['root-dir'] = '/opt/open-hackathon'

default['open-hackathon-ui']['git']['repository'] = "git@github.com:msopentechcn/open-hackathon.git"
default['open-hackathon-ui']['git']['revision'] = "master"

default['open-hackathon-ui']['hackathon-log'] = '/var/log/open-hackathon'

default['open-hackathon-ui']['uwsgi']['log-dir'] = '/var/log/uwsgi'
default['open-hackathon-ui']['uwsgi']['home_path'] = "/opt/open-hackathon/open-hackathon-templeUI/src"
default['open-hackathon-ui']['uwsgi']['config_file'] = "/opt/open-hackathon/nginx_openhackathon.uwsgi.ini"
default['open-hackathon-ui']['uwsgi']['base'] = "/opt/open-hackathon/open-hackathon-tempUI/src"
default['open-hackathon-ui']['uwsgi']['pythonpath'] = '/opt/open-hackathon/open-hackathon-tempUI/src'
default['open-hackathon-ui']['uwsgi']['http-port'] = '80'
default['open-hackathon-ui']['uwsgi']['logto'] = '/var/log/uwsgi/%n.log'

