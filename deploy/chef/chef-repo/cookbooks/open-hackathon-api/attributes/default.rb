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
default['openhackathon']['git']['checkout_branch'] = 'deploy'
default['openhackathon']['git']['known_hosts'] = "|1|BT8mM19S5ByEpm7VhLCODAlSlKY=|cd/jfFmnSeZi3cVRyJEJDNv5GA0= ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ=="

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
default['openhackathon']['gitcafe']['domain'] = 'https://gitcafe.com'
default['openhackathon']['gitcafe']['api_domain'] = 'https://api.gitcafe.com'

default['openhackathon']['weibo']['meta_content'] = 'ae884e09bc02b700'
default['openhackathon']['weibo']['client_id'] = ''
default['openhackathon']['weibo']['client_secret'] = ''
default['openhackathon']['weibo']['grant_type'] = 'authorization_code'
default['openhackathon']['weibo']['scope'] = 'all'

default['openhackathon']['token_expiration_minutes'] = '60*24'

# azure attributes
default['openhackathon']['azure']['subscriptionId'] = '31e6e137-4656-4f88-96fb-4c997b14a644'
default['openhackathon']['azure']['certPath'] = '/opt/openhackathon/open-hackathon/src/hackathon/certificates/1-31e6e137-4656-4f88-96fb-4c997b14a644.pem'
default['openhackathon']['azure']['managementServiceHostBase'] = 'management.core.chinacloudapi.cn'

# guacamole attributes
default['openhackathon']['guacamole']['host'] = 'http://localhost:8080'


# db installation attributes
default['openhackathon']['mysql']['service'] = 'openhackathon'
default['openhackathon']['mysql']['default_storage_engine'] = 'INNODB'
default['openhackathon']['mysql']['collation_server'] = 'utf8_general_ci'
default['openhackathon']['mysql']['initial_root_password'] = 'root'
default['openhackathon']['mysql']['version'] = '5.5'
default['openhackathon']['mysql']['port'] = '3307'

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

#data bags secret path
default['openhackathon'][:secret][:secretpath] = '/tmp/data_bag_key'
