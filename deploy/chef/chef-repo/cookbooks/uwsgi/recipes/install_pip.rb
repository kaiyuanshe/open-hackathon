include_recipe "uwsgi::_common_install"

include_recipe "python"

case node["uwsgi"]["version"]
when "lts"
  python_pip "uwsgi" do
    package_name "http://projects.unbit.it/downloads/uwsgi-lts.tar.gz"
  end
else
  python_pip "uwsgi" do
    action :install
    version node["uwsgi"]["version"] if node["uwsgi"]["version"]
  end
end
