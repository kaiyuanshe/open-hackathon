<<<<<<< HEAD
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#  
# The MIT License (MIT)
#  
=======
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#
# The MIT License (MIT)
#
>>>>>>> opentech/master
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
<<<<<<< HEAD
#  
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#  
=======
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
>>>>>>> opentech/master
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
<<<<<<< HEAD
# -----------------------------------------------------------------------------------
=======

>>>>>>> opentech/master
default['open-hackathon-api']['qq']['OAUTH_STATE'] = 'openhackathon'

default['open-hackathon-api']['mysql']['host'] = '127.0.0.1'
default['open-hackathon-api']['mysql']['user'] = 'hackathon'
default['open-hackathon-api']['mysql']['user-host'] = '%'
default['open-hackathon-api']['mysql']['pwd']  = 'hackathon'
default['open-hackathon-api']['mysql']['db']   = 'hackathon'
default['open-hackathon-api']['mysql']['setup-file'] = '/opt/open-hackathon/open-hackathon/src/setup_db.py'

default['open-hackathon-api']['environment'] = 'local'

default['open-hackathon-api']['token_expiration_minutes'] = '60*24'

default['open-hackathon-api']['azure']['subscriptionId'] = '31e6e137-4656-4f88-96fb-4c997b14a644'
default['open-hackathon-api']['azure']['certPath'] = '/home/if/If/LABOSS/open-hackathon/src/hackathon/certificates/1-31e6e137-4656-4f88-96fb-4c997b14a644.pem'
default['open-hackathon-api']['azure']['managementServiceHostBase'] = 'management.core.chinacloudapi.cn'

default['open-hackathon-api']['guacamole']['host'] = 'http://localhost:8080'

default['open-hackathon-api']['scheduler']['job_store'] = 'mysql'

default['open-hackathon-api']['git']['repository'] = 'git@github.com:msopentechcn/open-hackathon.git'
default['open-hackathon-api']['git']['revision'] = 'master'

default['open-hackathon-api']['mysql']['default_storage_engine'] = 'INNODB'
default['open-hackathon-api']['mysql']['collation_server'] = 'utf8_general_ci'
default['open-hackathon-api']['mysql']['initial_root_password'] = 'admin123'
default['open-hackathon-api']['mysql']['version'] = '5.5'
default['open-hackathon-api']['mysql']['port'] = '3310'


default['open-hackathon-api']['user'] = 'openhackathon'

default['open-hackathon-api']['uwsgi']['base'] = '/opt/open-hackathon/open-hackathon/src'
default['open-hackathon-api']['uwsgi']['pythonpath'] = '/opt/open-hackathon/open-hackathon/src'
default['open-hackathon-api']['uwsgi']['http-port'] = '80'
default['open-hackathon-api']['uwsgi']['logto-dir'] = '/var/log/uwsgi'
default['open-hackathon-api']['uwsgi']['logto'] = '/var/log/uwsgi/%n.log'

default['open-hackathon-api']['root-dir'] = '/opt/open-hackathon'

default['open-hackathon-api']['gem']['delete1'] = 'https://rubygems.org/'
default['open-hackathon-api']['gem']['delete2'] = 'http://rubygems.org/'
default['open-hackathon-api']['gem']['add'] = 'https://ruby.taobao.org/'

