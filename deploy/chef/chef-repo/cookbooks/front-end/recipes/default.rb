#
# Cookbook Name:: front-end
# Recipe:: default
#
# Copyright 2015, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

include_recipe "apt"
include_recipe "python"
#'pythton-setuptools'
package 'libmysqlclient-dev'
package 'libpcre3'
package 'libpcre3-dev'

include_recipe "git"
include_recipe "uwsgi"

directory '/opt/open-hackathon' do
  owner 'openhackathon'
  group 'openhackathon'
  mode '0755'
  action :create
end

git "/opt/open-hackathon" do
  repository "https://github.com/msopentechcn/open-hackathon.git"
  revision "master" 
  action :sync
end

directory '/var/log/uwsgi' do
  owner 'openhackathon'
  group 'openhackathon'
  mode '0744'
  action :create
end

directory '/var/log/open-hackathon' do
  owner 'openhackathon'
  owner 'openhackathon'
  mode '0744'
  action :create
end

python_pip "werkzeug" do
  version "0.9.6"
end

%w{ flask flask-restful flask-login flask-debugtoolbar }.each do |f|
  python_pip "#{f}"
end

template '/opt/open-hackathon/nginx_openhackathon.uwsgi.ini' do
  source 'uwsgi.ini.erb'
end

template '/etc/init.d/uwsgi' do
  source 'uwsgi.erb'
  owner 'openhackathon'
  group 'openhackathon'
  mode '0644'
end

template '/opt/open-hackathon/open-hackathon-tempUI/src/hackathon/config.py' do
  source 'config.py.erb'
end

uwsgi_service 'app' do
  home_path "/opt/open-hackathon/open-hackathon-templeUI/src"
  config_file "/opt/open-hackathon/nginx_openhackathon.uwsgi.ini"
  config_type :ini
end

