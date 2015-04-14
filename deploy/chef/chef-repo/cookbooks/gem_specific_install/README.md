# gem_specific_install cookbook

# Requirements

## Cookbooks

* git

# Usage
This will maintain a Git repo on /var/chef/cache and will update only if needed
```
include_recipe "gem_specific_install"
gem_specific_install "inifile" do
  repository "https://github.com/optiflows/inifile.git"
  revision "master"
end
```

These commands will run `gem specific_install`:
```
include_recipe "gem_specific_install"
chef_gem "inifile" do
  provider Chef::Provider::Package::Rubygems::SpecificInstall
  options( :repo => "https://github.com/optiflows/inifile.git")
end
```

```
include_recipe "gem_specific_install"
gem_package "inifile" do
  provider Chef::Provider::Package::Rubygems::SpecificInstall
  options( :repo => "https://github.com/optiflows/inifile.git", :branch => "master")
end
```

# Attributes

# Recipes

# Author

Author:: Guilhem Lettron (<guilhem.lettron@optiflows.com>)
