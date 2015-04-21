#
# Cookbook Name:: front-end
# Recipe:: default
#
# Copyright 2015, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

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
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------
user node['open-hackathon-adminUI']['sys_user']

include_recipe "apt"
include_recipe "python"
include_recipe "gcc"
#'pythton-setuptools'
package 'libmysqlclient-dev'
package 'libpcre3'
package 'libpcre3-dev'
package 'mysql-client-core'

include_recipe "git"
include_recipe "uwsgi"

directory node['open-hackathon-api']['root-dir'] do
  owner node['open-hackathon-adminUI']['sys_user']
  group node['open-hackathon-adminUI']['sys_user']
  mode '0755'
  action :create
end

git node['open-hackathon-api']['root-dir'] do
  repository node['open-hackathon-adminUI']['git']['repository']
  revision node['open-hackathon-adminUI']['git']['revision']
  action :sync
  timeout 60
end

directory node['open-hackathon-api']['uwsgi']['logto-dir'] do
  owner node['open-hackathon-adminUI']['sys_user']
  group node['open-hackathon-adminUI']['sys_user']
  mode '0744'
  action :create
end

directory node['open-hackathon-api']['uwsgi']['hacka-logto-dir'] do
  owner node['open-hackathon-adminUI']['sys_user']
  owner node['open-hackathon-adminUI']['sys_user']
  mode '0744'
  action :create
end

python_pip "werkzeug" do
  version "0.9.6"
end

python_pip "mock" do
  version "1.0.1"
end

%w{ flask flask-sqlalchemy flask-debugtoolbar flask-login sqlalchemy mysql-python wsgilog jinja2 six requests}.each do |f|
  python_pip "#{f}"
end

template node['open-hackathon-api']['root-dir']+'/nginx_openhackathon.uwsgi.ini' do
  source 'uwsgi.ini.erb'
end

template node['open-hackathon-api']['root-dir']+'/open-hackathon-adminUI/src/app/config.py' do
  source 'config.py.erb'
end

uwsgi_service 'app' do
  home_path node['open-hackathon-api']['root-dir']+'/open-hackathon-adminUI/src'
  config_file node['open-hackathon-api']['root-dir']+'/nginx_openhackathon.uwsgi.ini'
  config_type :ini
  start_immediately false
end

service 'uwsgi-app' do
  action :restart
end

