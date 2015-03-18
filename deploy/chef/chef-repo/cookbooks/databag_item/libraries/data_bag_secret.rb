module Autodesk
  module Chef
    module DataBagSecret
      extend self

      def load_databag_secret(node)
        source = node[:databag_item][:secret_source]
        path = node[:databag_item][:path]
        ::Chef::Log.info "Load databag secret from #{source}: #{path}"

        secret = load_secret(source, path, node)
        secret = secret.strip unless secret == nil

        secret
      end

      def load_secret(source, path, node)
        if 'none'.casecmp(source) == 0
          nil
        elsif 'local'.casecmp(source) == 0 then
          get_from_local(path)
        elsif 's3'.casecmp(source) == 0 then
          get_from_citadel(node[:databag_item][:bucket], path, node)
        elsif 'http'.casecmp(source) == 0 then
          get_from_http URI(path)
        else
          raise "Unknown secret source: #{source}" 
        end
      end

      def get_from_local(path)
        ::Chef::EncryptedDataBagItem.load_secret(path)
      end

      def get_from_citadel(bucket, path, node)

        node.override['citadel']['access_key_id'] = node[:databag_item][:username]
        node.override['citadel']['secret_access_key'] = node[:databag_item][:password]

        # Remove tailing '\n'
        Citadel.new(node, bucket)[path]
      end

      def get_from_http(uri)
        require 'net/http'
        Net::HTTP.get(uri)
      end

    end
  end
end
