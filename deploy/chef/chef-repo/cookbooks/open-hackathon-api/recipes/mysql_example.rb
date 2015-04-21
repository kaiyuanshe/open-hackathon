execute "exe-sql" do
  command "mysql -u#{node['open-hackathon-api']['mysql']['user']} -h#{node['open-hackathon-api']['mysql']['host']} -P#{node['open-hackathon-api']['mysql']['port']} -p#{node['open-hackathon-api']['mysql']['pwd']} #{node['open-hackathon-api']['mysql']['db']} < #{node['open-hackathon-api']['mysql']['sql-file']}"
end
