Description
===========

Opscode Chef cookbook that installs and configures uWSGI.
uWSGI is a fast, self-healing and developer/sysadmin-friendly application container server coded in pure C.

Requirements
============

Platform
--------
* Debian, Ubuntu

Cookbooks
---------
* python
* runit

Definitions
==========

`uwsgi_service`

-  `:home_path`         - path to the app you want to run with uWSGI, default to `"/var/www/app"`
-  `:pid_path`          - path to pid file for uWSGI, default to `"/var/run/uwsgi-app.pid"`
-  `:config_file`       - path to configuration file, default to `nil`, overrides the below options if not `nil`
-  `:config_type`       - configuration file type, default to `:ini`
-  `:host`              - hostname to run uWSGI on, default to `"127.0.0.1"`
-  `:port`              - port number to run uWSGI on, default to `8080`
-  `:worker_processes`  - number of uWSGI workers, default to `2`, should probably be relative to the number of CPUs
-  `:app`               - app to run on uwsgi, passed to --module parameted of uWSGI, default to `"main:app"`
-  `:uid`               - user-id to run uwsgi under, default to `"www-data"`
-  `:gid`               - group-id to run uwsgi under, default to `"www-data"`
-  `:master`            - enable uwsgi master process, default to `false`
-  `:no_orphans`        - kill workers without a master process, default to `false`
-  `:die_on_term`       - make uwsgi die on term signal, default to `false`
-  `:close_on_exec`     - set close-on-exec flag on uwsgi socket, default to `false`
-  `:lazy`              - load application after worker fork(), default to `false`
-  `:disable_logging`   - disable uwsgi request logging, default to `false`
-  `:start_immediately` - decide whether you want to start the service immediately or later manually, default to `true`

Usage
=====

Add the default uWSGI recipe to install uwsgi through pip.
Define a uWSGI service with a definition like so:

```ruby
uwsgi_service "myapp" do
  home_path "/var/www/app"
  pid_path "/var/run/uwsgi-app.pid"
  host "127.0.0.1"
  port 8080
  worker_processes 2
  app "flask:app"
end
```

You can also use a preexisting uWSGI configuration like so:

```ruby
uwsgi_service "myapp" do
  home_path "/var/www/app"
  pid_path "/var/run/uwsgi-app.pid"
  config_file "/etc/uwsgi/myapp.yaml"
  config_type :yaml
end
```

If `:config_file` is passed, all other options except `:home_path`, `:pid_path`, and `:config_type` are ignored.
