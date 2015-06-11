# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#  
# The MIT License (MIT)
#  
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

package 'libmysqlclient-dev'

include_recipe "open-hackathon-api::user"

service_name=node['openhackathon']['mysql']['service']

mysql_service service_name do
  run_group node['openhackathon']['user']
  run_user node['openhackathon']['user']
  initial_root_password api_creds["mysql_ini_pwd"]
  version node['openhackathon']['mysql']['version']
  port node['openhackathon']['mysql']['port']
  action [:create, :start]
end

mysql_config 'default' do
  config_name 'default'
  instance service_name
  source 'api.my.cnf.erb'
  notifies :restart, "mysql_service[#{service_name}]", :immediately
  action :create
end
