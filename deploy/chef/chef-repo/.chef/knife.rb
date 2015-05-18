# See http://docs.chef.io/config_rb_knife.html for more information on knife configuration options

# override 'user' in case your user name of chef server didn't match your local login
user = ENV['OPSCODE_USER'] || ENV['USER']
home_dir = ENV['HOME']


current_dir = File.dirname(__FILE__)
log_level                :info
log_location             STDOUT
node_name                "ice"
client_key               "/etc/chef/ice.pem"
validation_client_name   "msot-validator"
validation_key           "#{current_dir}/msot-validator.pem"
chef_server_url          "https://chef-hack.chinacloudapp.cn/organizations/msot"
syntax_check_cache_path  "#{ENV['HOME']}/.chef/syntaxcache"
cookbook_path            ["#{current_dir}/../cookbooks"]
ookbook_path            ["#{current_dir}/../cookbooks"]


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
