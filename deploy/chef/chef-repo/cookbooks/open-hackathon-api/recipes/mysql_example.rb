api_secret = Chef::EncryptedDataBagItem.load_secret("#{node['openhackathon'][:secret][:secretpath]}")
api_creds = Chef::EncryptedDataBagItem.load(node.chef_environment,"secret",api_secret)

execute "exe-sql" do
  command "mysql -u#{node['open-hackathon-api']['mysql']['user']} -h#{node['open-hackathon-api']['mysql']['host']} -P#{node['open-hackathon-api']['mysql']['port']} -p#{api_creds["mysql_usr_pwd"]} #{node['open-hackathon-api']['mysql']['db']} < #{node['open-hackathon-api']['mysql']['sql-file']}"
end
