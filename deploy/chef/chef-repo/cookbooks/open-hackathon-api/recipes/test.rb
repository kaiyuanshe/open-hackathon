mysql_service 'foo1' do
  initial_root_password 'admin123'
  version '5.5'
  port '9023'
  action [:create, :start]
end

mysql_config 'foo1' do
  instance 'foo1'
  source 'api.my.cnf.erb'
  notifies :restart, "mysql_service[foo1]", :immediately
  variables(
    :socket_file => "/var/run/mysql-foo1/mysqld.sock"
  )
  action :create
end
