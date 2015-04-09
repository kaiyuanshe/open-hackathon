mysql_service 'default' do
 # default_storage_engine "<%= node['open-hackathon-api']['mysql']['default_storage_engine']%>"
 # collation_server "<%= node['open-hackathon-api']['mysql']['collation_server']%>"
 # socket '/run/mysql:wq'
  charset 'utf8'
  run_group 'zhou'
  run_user 'zhou'
  initial_root_password 'admin12345'
  version '5.5'
  port '3307'
  action [:create, :start]
end

#mysql_config 'default9' do 
#  config_name 'default9'
#  charset  'utf8'
#  instance 'default9'
#  source 'my.cnf.erb'
#  notifies :restart, 'mysql_service[default9]', :immediately
#  action :create
#end
