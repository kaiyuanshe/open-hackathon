#
# Cookbook Name:: front-end
# Recipe:: default
#
# Copyright 2015, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#
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

directory '/opt/open-hackathon' do
  owner node['open-hackathon-adminUI']['sys_user']
  group node['open-hackathon-adminUI']['sys_user']
  mode '0755'
  action :create
end

git "/opt/open-hackathon" do
  repository node['open-hackathon-adminUI']['git']['repository']
  revision node['open-hackathon-adminUI']['git']['revision']
  action :sync
end

directory '/var/log/uwsgi' do
  owner node['open-hackathon-adminUI']['sys_user']
  group node['open-hackathon-adminUI']['sys_user']
  mode '0744'
  action :create
end

directory '/var/log/open-hackathon' do
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

template '/opt/open-hackathon/nginx_openhackathon.uwsgi.ini' do
  source 'uwsgi.ini.erb'
end

template '/etc/init.d/uwsgi' do
  source 'uwsgi.erb'
  owner node['open-hackathon-adminUI']['sys_user']
  group node['open-hackathon-adminUI']['sys_user']
  mode '0644'
end

template '/opt/open-hackathon/open-hackathon-adminUI/src/app/config.py' do
  source 'config.py.erb'
end

uwsgi_service 'app' do
  home_path "/opt/open-hackathon/open-hackathon-adminUI/src"
  config_file "/opt/open-hackathon/nginx_openhackathon.uwsgi.ini"
  config_type :ini
  start_immediately false
end

service 'uwsgi-app' do
  action :restart
end

