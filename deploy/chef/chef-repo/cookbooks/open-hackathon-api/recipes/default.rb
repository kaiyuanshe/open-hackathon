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
#  
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------
api_secret = Chef::EncryptedDataBagItem.load_secret("#{node['openhackathon'][:secret][:secretpath]}")
api_creds = Chef::EncryptedDataBagItem.load(node.chef_environment,"secret",api_secret)

include_recipe "python"
package 'libpcre3'
package 'libpcre3-dev'
include_recipe "uwsgi"

node.set['build_essential']['compile_time'] = true
include_recipe "build-essential"

include_recipe "open-hackathon-api::source"

requirement_file_dir = node['openhackathon'][:base_dir]+"/open-hackathon"
bash 'pip install for api' do
  cwd requirement_file_dir
  command 'pip install -r requirement.txt'
end

template node['openhackathon']['api']['src_dir']+'/nginx_hack_api.uwsgi.ini' do
  source 'uwsgi.ini.erb'
  owner node['openhackathon']['user']
  group node['openhackathon']['user']
  mode "0644"
end

template node['openhackathon']['api']['src_dir']+'/hackathon/config.py' do
  source 'config.py.erb'
  owner node['openhackathon']['user']
  group node['openhackathon']['user']
  variables( :mysql_usr_pwd => api_creds["mysql_usr_pwd"] )
  mode "0644"
end

uwsgi_service 'open-hackathon-api' do
  home_path node['openhackathon']['api']['src_dir']
  config_file node['openhackathon']['api']['src_dir']+'/nginx_hack_api.uwsgi.ini'
  config_type :ini
  uid node['openhackathon']['user']
  gid node['openhackathon']['user']
  start_immediately false
end

if node['openhackathon']['service']['start'] 
  service 'uwsgi-open-hackathon-api' do
    action :restart
  end
end
