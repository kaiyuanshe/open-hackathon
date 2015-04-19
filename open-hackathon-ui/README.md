
#Install nodejs
```shell
wget http://nodejs.org/dist/v0.10.35/node-v0.10.35-linux-x64.tar.gz
tar zxvf node-v0.10.35-linux-x64.tar.gz
sudo ln -s /home/{username}/node-v0.10.35-linux-x64/bin/node /usr/local/bin/node
sudo ln -s /home/{username}/node-v0.10.35-linux-x64/bin/npm /usr/local/bin/npm
```
Change the _{username}_ of the current user name.

#Install yo bower grunt-cli 
```shell
sudo npm install -g yo bower grunt-cli
sudo chown -R $(whoami) ~/.npm
```

#Bower and npm install
```shell
cd open-hackcthon-ui
bower install
npm install 
```
#Run grunt
```shell
grunt serve
```

##Grunt watch error - Waiting…Fatal error: watch ENOSPC
*echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p*
