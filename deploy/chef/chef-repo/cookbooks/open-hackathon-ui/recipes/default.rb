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

include_recipe "apt"
include_recipe "python"
package 'libmysqlclient-dev'
package 'libpcre3'
package 'libpcre3-dev'

include_recipe "git"
include_recipe "uwsgi"

directory node['open-hackathon-ui']['root-dir'] do
  owner node['open-hackathon-ui']['global-user']
  group node['open-hackathon-ui']['global-user']
  mode '0755'
  action :create
end

git node['open-hackathon-ui']['root-dir'] do
  repository node['open-hackathon-ui']['git']['repository']
  revision node['open-hackathon-ui']['git']['revision']
  action :sync
end

directory node['open-hackathon-ui']['uwsgi']['log-dir'] do
  owner node['open-hackathon-ui']['global-user']
  group node['open-hackathon-ui']['global-user']
  mode '0744'
  action :create
end

directory node['open-hackathon-ui']['hackathon-log'] do
  owner node['open-hackathon-ui']['global-user']
  owner node['open-hackathon-ui']['global-user']
  mode '0744'
  action :create
end

python_pip "werkzeug" do
  version "0.9.6"
end

%w{ flask flask-restful flask-login flask-debugtoolbar }.each do |f|
  python_pip "#{f}"
end

template node['open-hackathon-ui']['root-dir']+'/nginx_openhackathon.uwsgi.ini' do
  source 'uwsgi.ini.erb'
end

template node['open-hackathon-ui']['root-dir']+'/open-hackathon-tempUI/src/hackathon/config.py' do
  source 'config.py.erb'
end

uwsgi_service 'app' do
  home_path node['open-hackathon-ui']['uwsgi']['home_path']
  config_file node['open-hackathon-ui']['uwsgi']['config_file']
  config_type :ini
end

service 'uwsgi-app' do
  action :restart
end

