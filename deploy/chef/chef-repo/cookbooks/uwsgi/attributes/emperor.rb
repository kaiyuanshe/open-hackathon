default['uwsgi']['emperor']['conf_dir'] = "/etc/init.d/uwsgi"

case node['platform']
when "ubuntu", "debian"
 default['uwsgi']['emperor']['service'] = "upstart"
end
