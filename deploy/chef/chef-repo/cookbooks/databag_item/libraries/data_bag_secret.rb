# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


module MSOpentechCN
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
