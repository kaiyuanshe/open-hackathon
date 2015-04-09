actions :install
default_action :install

attribute :name, :kind_of => String, :name_attribute => true
attribute :file, :kind_of => String
attribute :parameters, :kind_of => Hash
