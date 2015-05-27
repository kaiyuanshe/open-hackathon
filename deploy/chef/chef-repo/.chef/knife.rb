# -*- coding: utf-8 -*-
#
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
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------

# See http://docs.chef.io/config_rb_knife.html for more information on knife configuration options

# override 'user' in case your user name of chef server didn't match your local login
user = ENV['OPSCODE_USER'] || ENV['USER']
home_dir = ENV['HOME']


current_dir = File.dirname(__FILE__)
log_level                :info
log_location             STDOUT
node_name                "#{user}"
client_key               "/etc/chef/#{user}.pem"
validation_client_name   "msot-validator"
validation_key           "#{current_dir}/msot-validator.pem"
chef_server_url          "https://chef-hack.chinacloudapp.cn/organizations/msot"
syntax_check_cache_path  "#{ENV['HOME']}/.chef/syntaxcache"
cookbook_path            ["#{current_dir}/../cookbooks"]


knife[:editor] = "vim"        
# Give it a chance for user to provide his personal override
#
# This is for the Build Agent where configuration is slightly different
# with Developer's workstation
#
require 'chef/config'
if File.exists?("#{home_dir}/.chef/knife.rb")
  Chef::Config.from_file("#{home_dir}/.chef/knife.rb")
end
