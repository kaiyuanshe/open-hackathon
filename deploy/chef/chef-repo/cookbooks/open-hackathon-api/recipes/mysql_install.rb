mysql_service 'default' do
  run_group node['open-hackathon-api']['user']
  run_user node['open-hackathon-api']['user']
  initial_root_password node['open-hackathon-api']['mysql']['initial_root_password']
  version node['open-hackathon-api']['mysql']['version']
  port node['open-hackathon-api']['mysql']['port']
  action [:create, :start]
end

mysql_config 'default' do 
  config_name 'default'
  instance 'default'
  source 'api.my.cnf.erb'
  notifies :restart, 'mysql_service[default]', :immediately
  action :create
end
