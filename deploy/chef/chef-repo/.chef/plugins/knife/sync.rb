require 'chef/knife'

module KnifePlugin
  class Sync < Chef::Knife

    banner "knife sync"

    option :environments,
      :short => '-e',
      :long => '--environments',
      :boolean => true,
      :description => "Update only environments"
    option :roles,
      :short => '-r',
      :long => '--roles',
      :boolean => true,
      :description => "Update only roles"
    option :nodes,
      :short => '-n',
      :long => '--nodes',
      :boolean => true,
      :description => "Update only nodes"
    option :databags,
      :short => '-D',
      :long => '--databags',
      :boolean => true,
      :description => "Update only databags"
    option :cookbooks,
      :short => '-c',
      :long => '--cookbooks',
      :boolean => true,
      :description => "Update only cookbooks"
    option :all,
      :short => '-a',
      :long => '--all',
      :boolean => true,
      :description => "Update all roles, environments, nodes, databags and cookbooks"

    deps do
      require 'pathname'
    end

    def run
      if config[:roles] 
        sync_object("roles/*", "role")
      elsif config[:environments]
        sync_object("environments/*", "environment")
      elsif config[:nodes]
        sync_object("nodes/*", "node")
      elsif config[:databags]
        sync_databag("data_bags/*", "data bag")
      elsif config[:cookbooks]
        sync_cookbooks()
      elsif config[:all]
        sync_object("roles/*", "role")
        sync_object("environments/*", "environment")
        sync_object("nodes/*", "node")
        sync_databag("data_bags/*", "data bag")
        sync_cookbooks()
      else
        ui.msg("Usage: knife sync --help")
      end
    end

    # Upload all cookbooks
    def sync_cookbooks()
      ui.msg("Uploading all cookbooks")
      result = `knife cookbook upload --all`
      ui.msg(result)
    end

    # Upload object based on input
    def sync_object(dirname,type)
      ui.msg("Finding type #{type} to upload from #{dirname}")
      upload_to_server(dirname,nil,type)
    end 

    # Upload databags...
    def sync_databag(dirname, type)
      ui.msg("Finding type #{type} to upload from #{dirname}")
      dirs = Dir.glob(dirname).select { |d| File.directory?(d) }
      dirs.each do |directory|
        dir = Pathname.new(directory).basename
        upload_to_server("#{directory}/*", dir, type)
      end 
    end

    # Common method to upload files to server
    def upload_to_server(dirpath, dir = nil, type)
      files = Dir.glob("#{dirpath}").select { |f| File.file?(f) }
      files.each do |file|
        fname = Pathname.new(file).basename
        if ("#{fname}".end_with?('.json') or "#{fname}".end_with?('.rb'))
          if dir.nil?
            ui.msg("Uploading #{type}: #{fname}")
            result = `knife #{type} from file #{fname}`
          else
            ui.msg("Uploading #{type}: #{dir}/#{fname}")
            result = `knife #{type} from file #{dir} #{fname}`
          end
        end 
      end 
    end

  end
end