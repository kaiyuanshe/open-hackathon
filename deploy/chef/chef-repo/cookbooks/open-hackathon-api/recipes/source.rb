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
include_recipe "git"
include_recipe "open-hackathon-api::user"

#temp ssh key for github. remove it after we open source it
directory "/home/#{node['openhackathon']['user']}/.ssh" do
  owner node['openhackathon']['user']
  group node['openhackathon']['user']
  mode  '0700'
  action :create
  recursive true
end
ssh_key_file="/home/#{node['openhackathon']['user']}/.ssh/id_rsa"
ssh_wrapper_file="/home/#{node['openhackathon']['user']}/.ssh/git_wrapper.sh"
template ssh_key_file do
  source 'temp.key.erb'
  owner node['openhackathon']['user']
  group node['openhackathon']['user']
  mode "0400"
end
file ssh_wrapper_file do
  owner node['openhackathon']['user']
  group node['openhackathon']['user']
  mode "0755"
  content "#!/bin/sh\nexec /usr/bin/ssh -i #{ssh_key_file} \"$@\""
end

directory node['openhackathon'][:base_dir] do
  owner node['openhackathon']['user']
  group node['openhackathon']['user']
  mode  '0755'
  action :create
end

file "/home/#{node['openhackathon']['user']}/.ssh/known_hosts" do
  owner node['openhackathon']['user']
  group node['openhackathon']['user']
  mode "0600"
  action :create
end

bash 'add known hosts' do
  user node['openhackathon']['user']
  cwd "/home/#{node['openhackathon']['user']}/.ssh"
  code <<-EOH
  ssh-keygen -H -R github.com
  echo "#{node['openhackathon']['git']['known_hosts']}" >> /home/#{node['openhackathon']['user']}/.ssh/known_hosts
  EOH
end

git node['openhackathon'][:base_dir] do
  repository node['openhackathon']['git']['repository']
  user node['openhackathon']['user']
  group node['openhackathon']['user']
  revision node['openhackathon']['git']['branch']
  checkout_branch node['openhackathon']['git']['checkout_branch']
  ssh_wrapper ssh_wrapper_file
  action :sync
  timeout 60
end

directory node['openhackathon']['uwsgi']['log_dir'] do
  owner node['openhackathon']['user']
  group node['openhackathon']['user']
  mode  '0744'
  action :create
end

directory node['openhackathon']['log_dir'] do
  owner node['openhackathon']['user']
  group node['openhackathon']['user']
  mode  '0744'
  action :create
end
