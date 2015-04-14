define :uwsgi_service,
    :home_path => "/var/www/app",
    :pid_path => "/var/run/uwsgi-app.pid",
    :host => "127.0.0.1",
    :port => 8080,
    :worker_processes => 2,
    :app => "main:app",
    :uid => "www-data",
    :gid => "www-data",
    :master => false,
    :no_orphans => false,
    :die_on_term => false,
    :close_on_exec => false,
    :lazy => false,
    :disable_logging => false,
    :threads => nil,
    :harakiri => nil,
    :stats => nil,
    :emperor => nil,
    :vacuum => false,
    :enable_threads => false,
    :buffer_size => nil,
    :config_file => nil,
    :config_type => :ini,
    :uwsgi_bin => '/usr/local/bin/uwsgi',
    :start_immediately => true do
  include_recipe "runit"

  # need to assign params to local vars as we can't pass params to nested definitions
  home_path = params[:home_path]
  pid_path = params[:pid_path]
  host = params[:host]
  port = params[:port]
  worker_processes = params[:worker_processes]
  app = params[:app]
  uid = params[:uid]
  gid = params[:gid]
  config_file = params[:config_file]
  config_type = params[:config_type]
  start_immediately = params[:start_immediately]
  extra_params = ""
  extra_params += " --master" if params[:master]
  extra_params += " --lazy" if params[:lazy]
  extra_params += " --no-orphans" if params[:no_orphans]
  extra_params += " --die-on-term" if params[:die_on_term]
  extra_params += " --close-on-exec" if params[:close_on_exec]
  extra_params += " --disable-logging" if params[:disable_logging]
  extra_params += " --enable-threads" if params[:enable_threads]
  extra_params += " --vacuum" if params[:vacuum]
  extra_params += " --threads %d" % [params[:threads]] if params[:threads]
  extra_params += " --harakiri %d" % [params[:harakiri]] if params[:harakiri]
  extra_params += " --stats %s" % [params[:stats]] if params[:stats]
  extra_params += " --emperor %s" % [params[:emperor]] if params[:emperor]
  extra_params += " --buffer-size %s" % [params[:buffer_size]] if params[:buffer_size]
  uwsgi_bin = params[:uwsgi_bin]

  runit_service "uwsgi-#{params[:name]}" do
    run_template_name "uwsgi"
    log_template_name "uwsgi"
    cookbook "uwsgi"
    restart_on_update start_immediately
    options ({
      :home_path => home_path,
      :pid_path => pid_path,
      :host => host,
      :port => port,
      :worker_processes => worker_processes,
      :app => app,
      :uid => uid,
      :gid => gid,
      :extra_params => extra_params,
      :uwsgi_bin => uwsgi_bin,
      :config_file => config_file,
      :config_type => config_type
    })
  end
end
