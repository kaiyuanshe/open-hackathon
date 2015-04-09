#
# Cookbook Name:: back-end
# Recipe:: default
#
# Copyright 2015, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#
include_recipe "apt"
include_recipe "python"
package 'libmysqlclient-dev'
package 'libpcre3'
package 'libpcre3-dev'
include_recipe "git"
include_recipe "uwsgi"

user node['open-hackathon-api']['user']

directory '/opt/open-hackathon' do
  owner node['open-hackathon-api']['user']
  group node['open-hackathon-api']['user']
  mode  '0755'
  action :create
end

git '/opt/open-hackathon' do
  repository node['open-hackathon-api']['git']['repository']
  revision node['open-hackathon-api']['git']['revision']
  action :sync
end

directory '/var/log/uwsgi' do
  owner node['open-hackathon-api']['user']
  group node['open-hackathon-api']['user']
  mode  '0744'
  action :create
end

python_pip "werkzeug" do
  version "0.9.6"
end

python_pip "flask-cors" do
  version "1.9.0"
end

python_pip "mock" do
  version "1.0.1"
end

%w{ flask flask-restful flask-admin sqlalchemy flask-sqlalchemy mysql-python wsgilog azure requests apscheduler }.each do |f|
  python_pip "#{f}"
end

template '/opt/open-hackathon/nginx_openhackathon.uwsgi.ini' do
  source 'uwsgi.ini.erb'
end


template '/opt/open-hackathon/open-hackathon/src/hackathon/config.py' do
  source 'config.py.erb'
end

uwsgi_service 'app' do
  home_path '/opt/open-hackathon/open-hackathon/src'
  config_file '/opt/open-hackathon/nginx_openhackathon.uwsgi.ini'
  config_type :ini
end
