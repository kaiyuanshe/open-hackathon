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
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

default['openhackathon']['environment'] = 'local'
default['openhackathon']['scheduler']['job_store'] = 'mysql'
default['openhackathon']['user'] = 'openhackathon'
default['openhackathon'][:base_dir] = '/opt/open-hackathon'

# scm attributes
default['openhackathon']['git']['repository'] = 'git@github.com:msopentechcn/open-hackathon.git'
default['openhackathon']['git']['branch'] = 'master'

# oauth attributes
default['openhackathon']['github']['client_id'] = ''
default['openhackathon']['github']['client_secret'] = ''
default['openhackathon']['github']['scope'] = 'user'

default['openhackathon']['qq']['OAUTH_STATE'] = 'openhackathon'
default['openhackathon']['qq']['client_id'] = ''
default['openhackathon']['qq']['client_secret'] = ''
default['openhackathon']['qq']['scope'] = 'get_user_info'
default['openhackathon']['qq']['response_type'] = 'code'
default['openhackathon']['qq']['grant_type'] = 'authorization_code'
default['openhackathon']['qq']['meta_content'] = ''

default['openhackathon']['gitcafe']['client_id'] = ''
default['openhackathon']['gitcafe']['client_secret'] = ''
default['openhackathon']['gitcafe']['response_type'] = 'code'
default['openhackathon']['gitcafe']['scope'] = 'public'
default['openhackathon']['gitcafe']['grant_type'] = 'authorization_code'
default['openhackathon']['gitcafe']['domain'] = ''
default['openhackathon']['gitcafe']['api_domain'] = ''

default['openhackathon']['weibo']['meta_content'] = 'ae884e09bc02b700'
default['openhackathon']['weibo']['client_id'] = ''
default['openhackathon']['weibo']['client_secret'] = ''
default['openhackathon']['weibo']['grant_type'] = 'authorization_code'
default['openhackathon']['weibo']['scope'] = 'all'

default['openhackathon']['token_expiration_minutes'] = '60*24'

# azure attributes
default['openhackathon']['azure']['subscriptionId'] = '31e6e137-4656-4f88-96fb-4c997b14a644'
default['openhackathon']['azure']['certPath'] = '/home/if/If/LABOSS/open-hackathon/src/hackathon/certificates/1-31e6e137-4656-4f88-96fb-4c997b14a644.pem'
default['openhackathon']['azure']['managementServiceHostBase'] = 'management.core.chinacloudapi.cn'

# guacamole attributes
default['openhackathon']['guacamole']['host'] = 'http://localhost:8080'


# db installation attributes
default['openhackathon']['mysql']['default_storage_engine'] = 'INNODB'
default['openhackathon']['mysql']['collation_server'] = 'utf8_general_ci'
default['openhackathon']['mysql']['initial_root_password'] = 'admin123'
default['openhackathon']['mysql']['version'] = '5.5'
default['openhackathon']['mysql']['port'] = '3310'

# db connection attributes
default['openhackathon']['mysql']['host'] = '127.0.0.1'
default['openhackathon']['mysql']['user_host'] = 'localhost'
default['openhackathon']['mysql']['user'] = 'hackathon'
default['openhackathon']['mysql']['password']  = 'hackathon'
default['openhackathon']['mysql']['db']   = 'hackathon'
default['openhackathon']['mysql']['setup_file'] = "#{openhackathon[:base_dir]}/open-hackathon/src/setup_db.py"
default['openhackathon']['mysql']['test_data_file'] = "#{openhackathon[:base_dir]}/open-hackathon/src/create_test_data.py"
default['openhackathon']['mysql']['sql_file'] = "#{openhackathon[:base_dir]}/setup_db.sql"

# container attributes
default['openhackathon']['api']['src_dir'] = "#{openhackathon[:base_dir]}/open-hackathon/src"
default['openhackathon']['api']['port'] = '15000'
default['openhackathon']['api']['endpoint'] = "http://localhost:#{openhackathon["api"]["port"]}"

# log
default['openhackathon']['log_dir'] = '/var/log/open-hackathon'
default['openhackathon']['uwsgi']['log_dir'] = '/var/log/uwsgi'

# mirror
default['openhackathon'][:npm][:enable_taobao_mirror] = true
default['openhackathon'][:gem][:enable_taobao_mirror] = true

default['open-hackathon-api']['gem']['delete1'] = 'https://rubygems.org/'
default['open-hackathon-api']['gem']['delete2'] = 'http://rubygems.org/'
default['open-hackathon-api']['gem']['add'] = 'https://ruby.taobao.org/'

