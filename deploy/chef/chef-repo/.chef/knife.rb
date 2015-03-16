user = ENV['OPSCODE_USER'] || ENV['USER']
home_dir = ENV['HOME']

current_dir = File.dirname(__FILE__)
chef_server_url          'http://abus-chef.aws.bluglu.net:4000'
log_level                :info
log_location             STDOUT
node_name                "#{user}"
client_key               "#{home_dir}/.chef/#{user}.pem"
validation_key           "#{home_dir}/.chef/validation.pem"
validation_client_name   'chef-validator'
cache_type               'BasicFile'
cache_options( :path => "#{home_dir}/.chef/checksums" )
cookbook_path            ["#{current_dir}/../cookbooks"]

knife[:aws_access_key_id] = "#{ENV['AWS_ACCESS_KEY_ID']}"
knife[:aws_secret_access_key] = "#{ENV['AWS_SECRET_ACCESS_KEY']}"

# Give it a chance for user to provide his personal override
# 
# This is for the Build Agent where configuration is slightly different
# with Developer's workstation
# 
require 'chef/config'
if File.exists?("#{home_dir}/.chef/knife.rb")
  Chef::Config.from_file("#{home_dir}/.chef/knife.rb")
end
