actions :install
default_action :install

attribute :gemname, :kind_of => String, :name_attribute => true
attribute :repository, :kind_of => String, :required => true
attribute :revision, :kind_of => String
