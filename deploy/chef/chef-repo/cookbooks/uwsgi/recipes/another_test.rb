uwsgi_service "app" do
  home_path "/opt/open-hackathon/open-hackathon-templeUI/src"
  config_file "/opt/open-hackathon/nginx_openhackathon.uwsgi.ini"
  config_type :ini
end
