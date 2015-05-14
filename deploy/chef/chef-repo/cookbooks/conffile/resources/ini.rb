actions :configure, :install
default_action :configure

attribute :path, :name_attribute => true, :kind_of => String, :required => true
attribute :parameters, :kind_of => Hash, :required => true
attribute :separator, :kind_of => String
attribute :comment, :kind_of => String
attribute :owner
attribute :group
attribute :mode

attr_accessor :installed, :configured
