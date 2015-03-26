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

include_recipe "tomcat"

if platform_family? "debian"
  # Packages require `apt-get update` before installing for unknown reasons
  include_recipe "apt"

  apt_update = true
  GUACAMOLE_DEB_PACKAGES.each do |pkg|
    package pkg do
      action :install
      options "--force-yes"  # *If* we use sourceforge packages, they are not signed
      notifies :run, "execute[apt-get-update]", :immediately if apt_update
    end
    apt_update = false
  end
end    

guacamole_war_url = node["guacamole"]["war"]["url"]
guacamole_webapp_dir = File.join(node["tomcat"]["webapp_dir"], "guacamole")
guacamole_war = "#{guacamole_webapp_dir}.war"

directory guacamole_webapp_dir do
  # Delete the webapp directory when a new war is deployed
  recursive true
  action :nothing
  notifies :restart, 'service[tomcat]'
end

if guacamole_war_url =~ Regexp.new('^http')
  # Regular web URL, use remote_file
  remote_file guacamole_war do
    source node["guacamole"]["war"]["url"]
    checksum node["guacamole"]["war"]["checksum"]
    user node['tomcat']['user']
    group node['tomcat']['group']
    mode '0644'
    notifies :delete, "directory[#{guacamole_webapp_dir}]", :immediately
  end

else
  # If the guacamole war file is local, cannot use remote_file
  cmd = "cp -f #{guacamole_war_url} #{guacamole_war}"
  execute cmd do
    not_if "cmp -s #{guacamole_war_url} #{guacamole_war}"
    notifies :delete, "directory[#{guacamole_webapp_dir}]", :immediately
  end
end

# This is a very private file, owned by root, but tomcat must be able
# to read it.
file '/etc/guacamole/user-mapping.xml' do
  user 'root'
  group node['tomcat']['group']
  mode '0640'
end

link "#{node['tomcat']['home']}/lib/guacamole.properties" do
  to "/etc/guacamole/guacamole.properties"
end

# Local Variables:
# ruby-indent-level: 2
# indent-tabs-mode: nil
# End:
