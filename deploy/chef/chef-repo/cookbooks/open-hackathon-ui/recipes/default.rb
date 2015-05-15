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
ui_secret = Chef::EncryptedDataBagItem.load_secret("#{node['openhackathon'][:secret][:secretpath]}")
ui_creds = Chef::EncryptedDataBagItem.load(node.chef_environment,"secret",ui_secret)

include_recipe "nodejs"
include_recipe "open-hackathon-api::source"
include_recipe 'logrotate'

# install npm packages
npm_packages = ["cnpm", "forever", "yo", "bower", "grunt-cli", "grunt-ng-annotate"]
if node['openhackathon'][:npm][:enable_taobao_mirror] then
  npm_packages.each do |pkg|
    nodejs_npm pkg do
      options ["--registry=https://registry.npm.taobao.org"]
    end
  end
else
  npm_packages.each do |pkg|
    nodejs_npm pkg
  end
end


template node['openhackathon'][:ui][:config_file] do
  source 'config.json.erb'
  owner node['openhackathon']['user']
  group node['openhackathon']['user']
  variables(
      :github_client_secret => ui_creds["github_client_secret"],
      :qq_client_secret  => ui_creds["qq_client_secret"],
      :gitcafe_client_secret => ui_creds["gitcafe_client_secret"],
      :weibo_client_secret => ui_creds["weibo_client_secret"]
    )
  mode "0644"
end

bash "config and build" do
  user node['openhackathon']['user']
  cwd node['openhackathon'][:ui][:src_dir]
  environment ({'HOME' => "#{node['openhackathon'][:ui][:src_dir]}"})
  timeout 600
  code <<-EOH
    bower install
    cnpm install
    grunt build
    EOH
end

service_name = "open-hackathon-ui"
start_script = "#{node['openhackathon'][:ui][:src_dir]}/app.js"
if node['openhackathon'][:ui][:debug] then
  start_script = "#{node['openhackathon'][:ui][:src_dir]}/dev.app.js"
end

service service_name do
  service_name service_name
  supports [:start, :stop, :restart, :status]
  action :nothing
end

template "/etc/init.d/#{service_name}" do
  source "initd.erb"
  owner 'root'
  group 'root'
  mode "0755"
  variables({
    :service_name => service_name,
    :description => "Open Hackathon platform UI",
    :start_script => "#{start_script}",
    :log_path => node['openhackathon'][:ui][:log][:log_file],
    :min_uptime => node['openhackathon'][:ui][:forever][:min_uptime],
    :spin_sleep_time => node['openhackathon'][:ui][:forever][:spin_sleep_time]
  })
  notifies :enable, "service[#{service_name}]"
  notifies :start, "service[#{service_name}]"
end

logrotate_app service_name do
  path node['openhackathon'][:ui][:log][:log_file]
  frequency node['openhackathon'][:ui][:log][:rotate_frequency]
  rotate node['openhackathon'][:ui][:log][:rotate]
  options ['missingok', 'compress', 'notifempty']
end
