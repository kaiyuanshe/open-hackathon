This document is about how to setup your local chef workstation.


### install chef
Please follow [Chef WorkStation Install Guide](http://docs.chef.io/client/install_workstation.html) to
install/configure your local machine as chef work station.

**_Notice that not all steps are required. Install chef client and configure ruby is enough_**


### signup
browse to chef [management console](https://open-hackathon-dev.chinacloudapp.cn). Choose _proceed_ in case certificate
error.

And then signup. You'd better signup with your local login user name. For example, my login to my dev machine is `foo`, then
I signup chef with the same username `foo`. If you signup with a different username ,say `bar`, you HAVE to change the knife
config file which located at `{src_root}/deploy/chef/chef-repo/.chef/knife.rb` and set variable `user` manually to `bar`.

next, contact the chef administrator to invite you to chef organizations. Later you will receive invitation on chef
management page. You need receive it.


### setup client cert
create directory `~/.chef` if not present.

after you sign in the management console, click `My Profile` in the top right corner. Click `reset key`, copy the private
key and save as `~/.chef/{username}.pem`.


### test the knife
change directory to `{src_root}/deploy/chef/chef-repo/.chef/`. You'd better always issue `knife ...` commands in this dir:
try some knife commands to see if it works:
```
knife client list
knife cookbook list
```
