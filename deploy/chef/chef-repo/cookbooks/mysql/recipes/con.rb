mysql_service 'default2' do
  #default_storage_engine "<%= node['open-hackathon-api']['mysql']['default_storage_engine']%>"
  #collation_server "<%= node['open-hackathon-api']['mysql']['collation_server']%>"
  #socket '/run/mysql:wq'
  #charset 'utf8'
  run_group 'zhou'
  run_user 'zhou'
  initial_root_password 'admin123'
  version '5.5'
  port '3310'
  action [:create, :start]
end

mysql_config 'default2' do 
  config_name 'default2'
  instance 'default2'
  source 'api.my.cnf.erb'
  notifies :restart, 'mysql_service[default2]', :immediately
  action :create
end
