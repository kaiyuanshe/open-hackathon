# -----------------------------------------------------------------------------------
#  
#  
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
api_secret = Chef::EncryptedDataBagItem.load_secret("#{node['openhackathon'][:secret][:secretpath]}")
api_creds = Chef::EncryptedDataBagItem.load(node.chef_environment,"secret",api_secret)

include_recipe "build-essential"

package "ruby-dev"
package "make"

if node['openhackathon'][:gem][:enable_taobao_mirror] then
  bash "setup ruby-gem url" do
    code <<-EOF
      gem source --remove https://rubygems.org/
      gem source --remove http://rubygems.org/
      gem source --remove https://ruby.taobao.org/
      gem source -a https://ruby.taobao.org/
    EOF
  end
end

mysql_client 'default' do
  version node['openhackathon']['mysql']['version']
  action :create
end

gem_package 'mysql2' do
  gem_binary RbConfig::CONFIG['bindir'] + '/gem' 
  timeout 60
  action :install
end

connection_info = {
  host: node['openhackathon']['mysql']['host'],
  port: node['openhackathon']['mysql']['port'],
  username: 'root',
  password: api_creds["mysql_ini_pwd"]
}

mysql_database node['openhackathon']['mysql']['db'] do
  connection connection_info
  provider  Chef::Provider::Database::Mysql
  action    :create
end

mysql_database_user node['openhackathon']['mysql']['user'] do
  connection connection_info
  host node['openhackathon']['mysql']['user_host']
  password api_creds["mysql_usr_pwd"]
  action :create
end

mysql_database_user node['openhackathon']['mysql']['user'] do
  connection connection_info
  database_name node['openhackathon']['mysql']['db']
  password api_creds["mysql_usr_pwd"]
  host node['openhackathon']['mysql']['user_host']
  privileges [:all]
  action :grant
end


filename = node['openhackathon']['mysql']['setup_file']
bash "setup_mysql" do
  code "sudo python #{filename}"
end

#sql_file=node['openhackathon']['mysql']['sql_file']
#execute "exe-sql" do
#  only_if "test -f #{sql_file}"
#  ignore_failure true
#  command "mysql -u#{node['openhackathon']['mysql']['user']} -h 127.0.0.1 -P#{node['openhackathon']['mysql']['port']} -p#{node['openhackathon']['mysql']['password']} #{node['openhackathon']['mysql']['db']} < #{sql_file}"
#end
