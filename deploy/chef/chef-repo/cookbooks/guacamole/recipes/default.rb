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

include_recipe "java"
include_recipe "tomcat"
include_recipe "open-hackathon-api::user"
include_recipe "open-hackathon-api::source"

GUACAMOLE_INSTALL_PACKAGES.each do |f|
  package "#{f}" do
    action :install
    options "--force-yes"
  end
end

guacamole_dir = node['guacamole']['dir']
guacamole_server_tar = node['guacamole']['server-tar']
guacamole_client_tar = node['guacamole']['client-tar']
guacamole_server_tar_extract_dir = node['guacamole']['server-tar-extract-dir'] 
guacamole_war_path = node['guacamole']['war-path']
configure_options = '--with-init-dir=/etc/init.d'

directory guacamole_dir do
  action :create
  owner node['tomcat']['user']
  group node['tomcat']['group']
  mode "0755" 
  recursive true
end

directory guacamole_server_tar_extract_dir do
  action :create
  owner node['tomcat']['user']
  group node['tomcat']['group']
  mode "0755" 
  recursive true
end

remote_file "#{guacamole_dir}/#{guacamole_server_tar}" do
  source node['guacamole']['server-tar-url']
  owner node['tomcat']['user']
  group node['tomcat']['group']
  mode "0644"
end

if node['guacamole']['use-local-war'] == 'true'
  cookbook_file node['guacamole']['war-cookbook-file'] do 
    path guacamole_war_path
    owner node['tomcat']['user']
    group node['tomcat']['group']
    mode "0644"
    action :create
  end
else
  remote_file guacamole_war_path do
    source node['guacamole']['war-url']
    owner node['tomcat']['user']
    group node['tomcat']['group']
    mode "0644"
  end
end

bash "guacamole-server-mount" do
  cwd guacamole_dir
  code <<-EOH
    ( cd #{guacamole_dir} && tar -xzf #{guacamole_dir}/#{guacamole_server_tar} -C #{guacamole_server_tar_extract_dir} && mv #{guacamole_server_tar_extract_dir}/*/* #{guacamole_server_tar_extract_dir} )
    ( cd #{guacamole_server_tar_extract_dir} && autoreconf -fi && ./configure #{configure_options} )
    ( cd #{guacamole_server_tar_extract_dir} && make && make install && ldconfig )
    /etc/init.d/guacd start
  EOH
end

directory node['guacamole']['tomcat-guacamole-share-folder'] do
  action :create
  owner node['tomcat']['user']
  group node['tomcat']['group']
  mode "0755" 
  recursive true
end

directory node['guacamole']['lib-directory'] do
  action :create
  owner node['tomcat']['user']
  group node['tomcat']['group']
  mode "0755"
  recursive true
end

template "#{node['guacamole']['lib-directory']}/#{node['guacamole']['properties']}" do
  source 'guacamole.properties.erb'
  mode '0644'
end

cookbook_file node['guacamole']['json-jar'] do 
  path "#{node['guacamole']['lib-directory']}/#{node['guacamole']['json-jar']}"
  owner node['tomcat']['user']
  group node['tomcat']['group']
  mode "0644"
  action :create
end

cookbook_file node['guacamole']['provider-jar'] do 
  path "#{node['guacamole']['lib-directory']}/#{node['guacamole']['provider-jar']}"
  owner node['tomcat']['user']
  group node['tomcat']['group']
  mode "0644"
  action :create
end

link "#{node['guacamole']['tomcat-guacamole-share-folder']}/#{node['guacamole']['properties']}" do 
  to "#{node['guacamole']['lib-directory']}/#{node['guacamole']['properties']}"
end

service "guacd" do 
  action :restart
end

service "tomcat7" do 
  action :restart
end
