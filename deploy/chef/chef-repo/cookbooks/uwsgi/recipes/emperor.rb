directory node['uwsgi']['emperor']['conf_dir'] do
  owner "root"
  group "root"
  mode "0755"
end

case node['uwsgi']['emperor']['service']
when "upstart"
  template "/etc/init/uwsgi.conf" do
    source "uwsgi_upstart.erb"
    owner "root"
    group "root"
    mode "0644"
    variables :config_dir => node['uwsgi']['emperor']['conf_dir']
    notifies :stop, "service[uwsgi]"
    notifies :start, "service[uwsgi]"
  end

  service "uwsgi" do
    provider Chef::Provider::Service::Upstart
    supports :status => true, :restart => true, :reload => true
    action [ :enable, :start ]
  end
end
