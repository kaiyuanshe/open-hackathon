include Chef::DSL::IncludeRecipe

# Support whyrun
def whyrun_supported?
  true
end

action :install do
  include_recipe "uwsgi::emperor"

  if new_resource.file
    converge_by ("Create #{new_resource.name} with remote_file") do
      remote_file "config file for #{new_resource.name}" do
        path ::File.join(node['uwsgi']['emperor']['conf_dir'], new_resource.name + ::File.extname(new_resource.file))
        source new_resource.file
        owner "root"
        group "root"
        mode "0644"
        notifies :reload, "service[uwsgi]"
      end
    end
  elsif new_resource.parameters
    include_recipe "conffile"
    converge_by ("Create #{new_resource.name} with conffile") do
      conffile_ini "config file for #{new_resource.name}" do
        path ::File.join(node['uwsgi']['emperor']['conf_dir'], "#{new_resource.name}.ini")
        parameters new_resource.parameters
        notifies :reload, "service[uwsgi]"
      end
    end
  end
end
