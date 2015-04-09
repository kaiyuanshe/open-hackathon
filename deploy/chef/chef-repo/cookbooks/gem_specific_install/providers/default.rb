use_inline_resources

include Chef::DSL::IncludeRecipe

require 'rubygems/specification'

action :install do
  include_recipe 'git'

  git path do
    repository new_resource.repository
    revision new_resource.revision if new_resource.revision
    notifies :create, "ruby_block[install gem #{new_resource.gemname}]", :immediately
  end

  ruby_block "install gem #{new_resource.gemname}" do
    block do
      require 'rubygems/dependency_installer'
      require 'rubygems/specification'

      ::Dir.chdir(path)
      gemspec = ::Gem::Specification.load(gemspec_file)
      gem = if RUBY_VERSION < '2.0.0'
              require 'rubygems/builder'
              Gem::Builder.new(gemspec).build
            else
              Gem::Package.build(gemspec)
            end
      inst = ::Gem::DependencyInstaller.new
      inst.install gem
      Gem.clear_paths
    end
    # install only on git update
    action :nothing
    only_if { ::File.exist?(gemspec_file) }
  end
end

def path
  ::File.join(Chef::Config[:file_cache_path], new_resource.gemname)
end

def gemspec_file
  ::File.join(path, "#{new_resource.gemname}.gemspec")
end

def already_installed?
  Gem::Specification.any? { |g| g.name == new_resource.gemname }
end
