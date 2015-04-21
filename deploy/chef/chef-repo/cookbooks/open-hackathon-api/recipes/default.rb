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
#  
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------


include_recipe "python"
package 'libpcre3'
package 'libpcre3-dev'
include_recipe "uwsgi"

node.set['build_essential']['compile_time'] = true
include_recipe "build-essential"

include_recipe "open-hackathon-api::source"

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

template node['openhackathon']['api']['src_dir']+'/nginx_hack_api.uwsgi.ini' do
  source 'uwsgi.ini.erb'
  owner node['openhackathon']['user']
  group node['openhackathon']['user']
  mode "0644"
end

template node['openhackathon']['api']['src_dir']+'/hackathon/config.py' do
  source 'config.py.erb'
  owner node['openhackathon']['user']
  group node['openhackathon']['user']
  mode "0644"
end

uwsgi_service 'app' do
  home_path node['openhackathon']['api']['src_dir']
  config_file node['openhackathon']['api']['src_dir']+'/nginx_hack_api.uwsgi.ini'
  config_type :ini
  uid node['openhackathon']['user']
  gid node['openhackathon']['user']
end
