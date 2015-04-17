# Knife plugin for edit databags

require 'chef/encrypted_data_bag_item'
require 'json'
require 'tempfile'

module Autodesk
  # Cleans up any defunct servers in Chef
  class DataBagEdit < Chef::Knife
    banner "knife data bag edit BAG [ITEM]"

    option :secret_file,
      :short => "-s SECRET-FILE",
      :long => "--secret-file  SECRET-FILE",
      :description => "Security file to encrypt/decrypt the databag"

    def run
        if name_args.empty? then
          show_usage
          exit 1
        end

        @data_bag = @name_args[0]
        @item_name = @name_args[1] || "default"

        if config[:secret_file] != nil then
          secret = load_secret_file(config[:secret_file])
        else
          secret = nil
        end

        ui.msg "Edit databag item '#{@data_bag}/#{@item_name}'  ..."
        edit_data_bag(@data_bag, @item_name, secret)
    end

    def edit_data_bag(data_bag, item_name, secret=nil)
      editor_configured?
      databag_item_path = "data_bags/#{data_bag}/#{item_name}.json"

      original_data = load_databag_item(databag_item_path, secret)
      new_data = edit_databag_item (original_data)

      if new_data == original_data then
        ui.msg 'No changes detected; not writing anything.'
        return;
      end

      save_databag_item(new_data, databag_item_path, secret)
    end

    def editor_configured?
      unless ENV['EDITOR']
        ui.fatal "No EDITOR found. Try:"
        ui.fatal "export EDITOR=vim"
        exit 1
      end
    end

    def load_secret_file(data_bag_key_path)
      if data_bag_key_path == nil then
        return nil
      end

      # Create secret file if it does not exist
      data_bag_key_path = File.join(Dir.pwd, data_bag_key_path)
      unless File.exists? data_bag_key_path
        ui.confirm("No data bag key found. Generate? ")
        generate_secret_file(data_bag_key_path)
      end

      Chef::EncryptedDataBagItem.load_secret(data_bag_key_path)
    end

    def generate_secret_file(data_bag_key_path)
      FileUtils.mkdir_p File.dirname(data_bag_key_path)
      puts 'Generating new data bag key. Don\'t forget to store it in a safe place!'
      `openssl rand -base64 512 >'#{data_bag_key_path}'`
    end

    def load_databag_item(databag_item_path, secret=nil)
      if not File.exists? databag_item_path then
        ui.msg "Cannot find #{File.join(Dir.pwd, databag_item_path)}; creating new data bag"
        return {'id' => @item_name}
      end

      data = JSON.parse(File.read(databag_item_path))

      # only decrypt when necessary
      if secret != nil then
        data = Chef::EncryptedDataBagItem.new(data, secret).to_hash
      end

      return data
    end

    def save_databag_item(data, databag_item_path, secret=nil) 
      if secret != nil then
        data = Chef::EncryptedDataBagItem.encrypt_data_bag_item(data, secret)
      end

      FileUtils.mkdir_p File.dirname(databag_item_path)
      File.write databag_item_path, JSON.pretty_generate(data)
    end

    def edit_databag_item(data)
      # decrypt file to a temp file for editing
      temp_file = Tempfile.new ["knife-data-bag-edit",".json"]
      at_exit { temp_file.delete }

      temp_file.puts JSON.pretty_generate(data)
      temp_file.close

      # edit data in the editor
      begin
        new_data = nil
        system "#{ENV['EDITOR']} #{temp_file.path}"
        begin
          new_data = JSON.parse(File.read(temp_file.path))
        rescue JSON::ParserError => e
          ui.msg "Error parsing data bag:\n\n#{e.message}.\n\nPress Return to continue editing the file."
          $stdin.gets
        end
      end while !new_data

      return new_data
    end
  end
end