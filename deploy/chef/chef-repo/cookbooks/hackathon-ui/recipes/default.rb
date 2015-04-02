#
# Cookbook Name:: front-end
# Recipe:: default
#
# Copyright (c) Microsoft Open Technologies, Inc.  All rights reserved.
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

