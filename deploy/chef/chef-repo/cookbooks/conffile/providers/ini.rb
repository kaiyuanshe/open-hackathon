use_inline_resources

include Chef::DSL::IncludeRecipe

action :configure do
  configure
end

action :install do
  install
end

def load_current_resource
  include_recipe 'conffile'

  require 'inifile'

  @current_resource = Chef::Resource::ConffileIni.new(@new_resource.name)
  @current_resource.name(@new_resource.name)
  @current_resource.parameters(@new_resource.parameters)
  if ini_equal?(@current_resource.parameters)
    @current_resource.installed = true
    @current_resource.configured = true
  elsif ini_include?(@current_resource.parameters)
    @current_resource.configured = true
  end
end

def install
  include_recipe 'conffile'
  ruby_block "Install #{current_resource.name}" do
    block do
      ini = IniFile.new(ini_params)
      ini.merge!(new_resource.parameters)
      ini.write(write_params)
    end
    not_if { current_resource.installed }
  end
  file_rights
end

def configure
  include_recipe 'conffile'

  ruby_block "Configure #{current_resource.name}" do
    block do
      IniFile.new(init_params).merge(new_resource.parameters).write
    end
    not_if { current_resource.configured }
  end
  file_rights
end

def file_rights
  file current_resource.path do
    owner new_resource.owner
    group new_resource.group
    mode new_resource.mode
  end
end

def ini_params
  hash = {}
  hash.merge!(:comment => new_resource.comment) if new_resource.comment
  hash.merge!(:param => new_resource.separator) if new_resource.separator
  hash
end

def write_params
  { :filename => new_resource.path }
end

def init_params
  write_params.merge(ini_params)
end

def ini_equal?(parameters)
  if ::File.exists?(new_resource.path)
    current_ini = IniFile.new(init_params)
    return true if current_ini.to_h == parameters
  end
  false
end

def ini_include?(parameters)
  if ::File.exists?(new_resource.path)
    current_ini = IniFile.new(init_params)
    return true if current_ini.to_h.merge(parameters) == current_ini
  end
  false
end
