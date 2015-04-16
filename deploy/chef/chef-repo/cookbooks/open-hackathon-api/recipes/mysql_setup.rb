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
include_recipe "build-essential"

package "ruby-dev"
package "make"

bash "setup ruby-gem url" do
  code <<-EOF
    gem source --remove https://rubygems.org/
    gem source --remove http://rubygems.org/
    gem source --remove https://ruby.taobao.org/
    gem source -a https://ruby.taobao.org/
  EOF
end

mysql_client 'default' do
  version node['open-hackathon-api']['mysql']['version'] 
  action :create
end

gem_package 'mysql2' do
  gem_binary RbConfig::CONFIG['bindir'] + '/gem' 
=======

mysql2_chef_gem 'default' do
  client_version node['open-hackathon-api']['mysql']['version']
>>>>>>> opentech/master
  action :install
end

connection_info = {
  host: '127.0.0.1',
  port: node['open-hackathon-api']['mysql']['port'],
  username: 'root',
  password: node['open-hackathon-api']['mysql']['initial_root_password']
}


mysql_database node['open-hackathon-api']['mysql']['db'] do
  connection connection_info
  provider  Chef::Provider::Database::Mysql
  action    :create
end

mysql_database_user node['open-hackathon-api']['mysql']['user'] do
  connection connection_info
  action :create
end

mysql_database_user node['open-hackathon-api']['mysql']['user'] do
  connection connection_info
  database_name node['open-hackathon-api']['mysql']['db']
  password node['open-hackathon-api']['mysql']['pwd']
  host node['open-hackathon-api']['mysql']['user-host']
  privileges [:all]
  action :grant
end

filename = node['open-hackathon-api']['mysql']['setup-file']

#python '/opt/open-hackathon/open-hackathon/src/setup_db.py' do
bash "setup_mysql" do
  code "python #{filename}"
end
