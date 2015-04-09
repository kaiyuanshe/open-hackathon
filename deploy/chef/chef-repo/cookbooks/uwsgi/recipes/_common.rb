#group node['uwsgi']['group'] do
#  system true
#end

#user node['uwsgi']['user'] do
#  supports :manage_home => true
#  gid node['uwsgi']['group']
#  home node['uwsgi']['path']
#  system true
#end
