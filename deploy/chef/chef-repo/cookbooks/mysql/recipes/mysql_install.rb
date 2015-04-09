mysql_service 'default' do
  run_group 'zhou'
  run_user 'zhou'
  initial_root_password 'admin123'
  version '5.5'
  port '3310'
  action [:create, :start]
end

mysql_config 'default' do 
  config_name 'default'
  instance 'default'
  source 'api.my.cnf.erb'
  notifies :restart, 'mysql_service[default]', :immediately
  action :create
end
