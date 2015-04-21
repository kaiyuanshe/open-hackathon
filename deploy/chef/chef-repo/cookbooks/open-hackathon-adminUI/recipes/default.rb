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
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

include_recipe "open-hackathon-api::source"

include_recipe "python"
# include_recipe "gcc"
package 'libmysqlclient-dev'
package 'libpcre3'
package 'libpcre3-dev'
package 'mysql-client-core'
include_recipe "uwsgi"


python_pip "werkzeug" do
  version "0.9.6"
end

python_pip "mock" do
  version "1.0.1"
end

%w{ flask flask-sqlalchemy flask-debugtoolbar flask-login sqlalchemy mysql-python wsgilog jinja2 six requests}.each do |f|
  python_pip "#{f}"
end

config_file= node['openhackathon']['admin']['src_dir']+'/nginx_openhackathon.uwsgi.ini'
template config_file do
  source 'uwsgi.ini.erb'
  owner node['openhackathon']['user']
  group node['openhackathon']['user']
  mode "0644"
end

template node['openhackathon']['admin']['src_dir']+'/app/config.py' do
  source 'config.py.erb'
  owner node['openhackathon']['user']
  group node['openhackathon']['user']
  mode "0644"
end

uwsgi_service 'app' do
  home_path node['openhackathon']['admin']['src_dir']
  config_file config_file
  config_type :ini
  start_immediately false
  uid node['openhackathon']['user']
  gid node['openhackathon']['user']
end

service 'uwsgi-app' do
  action :restart
end
