mysql2_chef_gem 'default' do
  client_version node['open-hackathon-api']['mysql']['version']
  action :install
end

connection_info = {
  host: '127.0.0.1',
  port: node['open-hackathon-api']['mysql']['port'],
  username: 'root',
  password: node['open-hackathon-api']['mysql']['initial_root_password']
}


mysql_database node['open-hackathon-api']['mysql']['db'] do
  connection connection_info
  provider  Chef::Provider::Database::Mysql
  action    :create
end

mysql_database_user node['open-hackathon-api']['mysql']['user'] do
  connection connection_info
  action :create
end

mysql_database_user node['open-hackathon-api']['mysql']['user'] do
  connection connection_info
  database_name node['open-hackathon-api']['mysql']['db']
  password node['open-hackathon-api']['mysql']['pwd']
  host node['open-hackathon-api']['mysql']['host']
  privileges [:all]
  action :grant
end

filename = node['open-hackathon-api']['mysql']['setup-file']


#python node['open-hackathon-api']['mysql']['setup-file'] do
python '/opt/open-hackathon/open-hackathon/src/setup_db.py' do
  action :run
end
