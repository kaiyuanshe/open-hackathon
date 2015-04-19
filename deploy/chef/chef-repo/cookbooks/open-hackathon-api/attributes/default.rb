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

default['open-hackathon']['environment'] = 'local'
default['open-hackathon']['scheduler']['job_store'] = 'mysql'
default['open-hackathon']['user'] = 'openhackathon'
default['open-hackathon'][:base_dir] = '/opt/open-hackathon'

# scm attributes
default['open-hackathon']['git']['repository'] = 'git@github.com:msopentechcn/open-hackathon.git'
default['open-hackathon']['git']['revision'] = 'master'

# oauth attributes
default['open-hackathon']['github']['client_id'] = '0f0e47f99e682730b68e'
default['open-hackathon']['github']['client_secret'] = 'ce1e4aa7f879a560e77b796b423789126b962cee'
default['open-hackathon']['github']['scope'] = 'user'

default['open-hackathon']['qq']['OAUTH_STATE'] = 'openhackathon'
default['open-hackathon']['qq']['client_id'] = '101200890'
default['open-hackathon']['qq']['client_secret'] = '88ad67bd4521c4cc47136854781cb9b5'
default['open-hackathon']['qq']['scope'] = 'get_user_info'
default['open-hackathon']['qq']['response_type'] = 'code'
default['open-hackathon']['qq']['grant_type'] = 'authorization_code'
default['open-hackathon']['qq']['meta_content'] = '274307566465013314076545663016134754100636'

default['open-hackathon']['gitcafe']['client_id'] = '1c33ecdf4dd0826325f60a92e91834522b1cdf47a7f90bdaa79f0526fdc48727'
default['open-hackathon']['gitcafe']['client_secret'] = '80b63609000b20c1260df28081c08712617648e1b528086bbb089f0af4614509'
default['open-hackathon']['gitcafe']['response_type'] = 'code'
default['open-hackathon']['gitcafe']['scope'] = 'public'
default['open-hackathon']['gitcafe']['grant_type'] = 'authorization_code'
default['open-hackathon']['gitcafe']['domain'] = 'https://gcs.dgz.sh'
default['open-hackathon']['gitcafe']['api_domain'] = 'https://gcas.dgz.sh'

default['open-hackathon']['weibo']['meta_content'] = 'ae884e09bc02b700'
default['open-hackathon']['weibo']['client_id'] = '1943560862'
default['open-hackathon']['weibo']['client_secret'] = 'a5332c39c129902e561bff5e4bcc5982'
default['open-hackathon']['weibo']['grant_type'] = 'authorization_code'
default['open-hackathon']['weibo']['scope'] = 'all'

default['open-hackathon']['token_expiration_minutes'] = '60*24'

# azure attributes
default['open-hackathon']['azure']['subscriptionId'] = '31e6e137-4656-4f88-96fb-4c997b14a644'
default['open-hackathon']['azure']['certPath'] = '/home/if/If/LABOSS/open-hackathon/src/hackathon/certificates/1-31e6e137-4656-4f88-96fb-4c997b14a644.pem'
default['open-hackathon']['azure']['managementServiceHostBase'] = 'management.core.chinacloudapi.cn'

# guacamole attributes
default['open-hackathon']['guacamole']['host'] = 'http://localhost:8080'


# db installation attributes
default['open-hackathon']['mysql']['default_storage_engine'] = 'INNODB'
default['open-hackathon']['mysql']['collation_server'] = 'utf8_general_ci'
default['open-hackathon']['mysql']['initial_root_password'] = 'admin123'
default['open-hackathon']['mysql']['version'] = '5.5'
default['open-hackathon']['mysql']['port'] = '3310'

# db connection attributes
default['open-hackathon']['mysql']['host'] = 'localhost'
default['open-hackathon']['mysql']['user'] = 'hackathon'
default['open-hackathon']['mysql']['password']  = 'hackathon'
default['open-hackathon']['mysql']['db']   = 'hackathon'
default['open-hackathon']['mysql']['setup-file'] = '#{open-hackathon[:base_dir]}/open-hackathon/src/setup_db.py'


# container attributes
default['open-hackathon']['api']['src_dir'] = '#{open-hackathon[:base_dir]}/open-hackathon/src'
default['open-hackathon']['api']['port'] = '80'

# log
default['open-hackathon']['log_dir'] = '/var/log/open-hackathon'
default['open-hackathon']['uwsgi']['log_dir'] = '/var/log/uwsgi'
default['open-hackathon']['uwsgi']['log_file'] = "#{open-hackathon['uwsgi']['log_dir']}/%n.log"

