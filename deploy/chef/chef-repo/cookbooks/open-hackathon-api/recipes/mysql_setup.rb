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

mysql2_chef_gem 'default' do
  client_version node['open-hackathon']['mysql']['version']
  action :install
end

connection_info = {
  host: '127.0.0.1',
  port: node['open-hackathon']['mysql']['port'],
  username: 'root',
  password: node['open-hackathon']['mysql']['initial_root_password']
}


mysql_database node['open-hackathon']['mysql']['db'] do
  connection connection_info
  provider  Chef::Provider::Database::Mysql
  action    :create
end

mysql_database_user node['open-hackathon']['mysql']['user'] do
  connection connection_info
  action :create
end

mysql_database_user node['open-hackathon']['mysql']['user'] do
  connection connection_info
  database_name node['open-hackathon']['mysql']['db']
  password node['open-hackathon']['mysql']['pwd']
  host node['open-hackathon']['mysql']['host']
  privileges [:all]
  action :grant
end


filename = node['open-hackathon']['mysql']['setup-file']
python '<%= node['open-hackathon']['api']['src_dir'] %>/setup_db.py' do
  action :run
end
