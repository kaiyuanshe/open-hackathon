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


include_recipe "nodejs"
include_recipe "open-hackathon-api::source"

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