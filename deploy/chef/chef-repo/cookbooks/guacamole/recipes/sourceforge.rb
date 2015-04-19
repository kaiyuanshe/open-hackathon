#
# Cookbook Name:: guacamole
# Recipe:: default
# Author:: Jeff Dutton (<jeff.dutton@stratus.com>)
#
# Copyright (C) 2012, Jeff Dutton
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.

# Append the RDP library package, which is not supported in default
# apt distro repository.
GUACAMOLE_DEB_PACKAGES << 'libguac-client-rdp0'

include_recipe "apt"

package "dpkg-dev"  # Needed to build local repository

guacamole_packages_dir = "/var/lib/guacamole/packages"
guacamole_packages_tgz = guacamole_packages_dir + ".tgz"
guacamole_sources_list = "/etc/apt/sources.list.d/guacamole.list"

directory guacamole_packages_dir do
  user 'root'
  group 'root'
  mode '0755'
  recursive true
end

remote_file guacamole_packages_tgz do
  source node["guacamole"]["sourceforge"]["url"]
  checksum node["guacamole"]["sourceforge"]["checksum"]
  user 'root'
  group 'root'
  mode '0644'
end

execute "clean guacamole packages directory" do
  # Clean out the packages directory immediately before untar
  command "rm -rf #{guacamole_packages_dir}/*"
  only_if { File.directory?(guacamole_packages_dir) }
  action :nothing
  subscribes :run, "remote_file["+guacamole_packages_tgz+"]", :immediately
end

execute "untar guacamole packages" do
  command "tar xzvf #{guacamole_packages_tgz} -C #{guacamole_packages_dir} --strip-components=1 --no-same-owner --no-same-permissions > #{guacamole_packages_dir}.untar.output"
  action :nothing
  subscribes :run, "execute[clean guacamole packages directory]", :immediately
end

# Apt Repository for the sourceforge guacamole packages
file guacamole_sources_list do
  user 'root'
  group 'root'
  mode '0644'
  content "deb file:#{guacamole_packages_dir} ./\n"
  action :nothing
end

execute "build guacamole repository" do
  command "dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz"
  cwd guacamole_packages_dir
  action :nothing
  not_if { File.size?("#{guacamole_packages_dir}/Packages.gz") }
  subscribes :run, "execute[untar guacamole packages]", :immediately
  notifies :create, "file["+guacamole_sources_list+"]", :immediately
  notifies :run, "execute[apt-get update]", :immediately
end

include_recipe "guacamole::default"

GUACAMOLE_DEB_PACKAGES.each do |pkg|
  package pkg do
    # Upgrade guacamole to the latest version in the new repository
    action :nothing
    options "--force-yes"  # *If* we use sourceforge packages, they are not signed
    subscribes :upgrade, "execute[build guacamole repository]"
  end
end

# Local Variables:
# ruby-indent-level: 2
# indent-tabs-mode: nil
# End:
