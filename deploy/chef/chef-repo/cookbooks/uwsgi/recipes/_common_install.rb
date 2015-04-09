case node['platform_family']
when 'debian'
  # needed for uwsgi starting with version 1.3
  package "libssl0.9.8"
end
