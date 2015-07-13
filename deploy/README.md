This document will tell you how to deploy the whole open-hackathon web application environment manually.    
And the whole environment cotains serval components such guacamole , nginx , tomcat and the open-hackathon running Dependencies. 
* [Introduction](#Introduction)
  * [What is OpenHackathon](#What-is-OpenHackathon)
  * [Why choose OpenHackathon](#Why-choose-OpenHackathon)
  * [Where is the feature](#Where-is-the-feature)
* [User's Guide](#User's-Guide)
  *[introduction vedio](#introduction-vedio)
* [Developer's Guide](#Developer's-Guide)
  * [setup develop environment](#setup-develop-environment)
    * [setup system components](#install-system-components)
    * [setup Docker Env](#setup-Docker-Env)
    * [setup Guacamole Env](#setup-Guacamole-Env)
    * [get src from GitHub](#get-src-from-GitHub)
    * [setup MysqlDB Env](#setup-MysqlDB-Env)
    * [setup server api Env](#setup-server-api-Env)
    * [setup frontend website Env](#setup-frontend-website-Env)
* [QA](#QA)

# Introduction
# User's Guide
## introduction vedio
# Developer's Guide
## setup develop environment

#install system components
```shell
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install build-essential python python-dev python-setuptools libmysqlclient-dev
sudo apt-get install vim git
sudo easy_install pip
sudo apt-get install tomcat7
sudo apt-get install openjdk-7-jdk
sudo apt-get install nginx
sudo apt-get install mysql-server

```
#Get src from github
```
cd /opt/
git clone https://github.com/msopentechcn/open-hackathon.git
```

#config guacamole
Do this steps you should follow [http://guac-dev.org/doc/gug/installing-guacamole.html](http://guac-dev.org/doc/gug/installing-guacamole.html)      
Here are the main steps about configure and depoly guacamole-server as well as guacamole-client       
Note：*guacamole version choose 0.9.3 !!!*


###setup guacamole-server
```
sudo apt-get install libtool libcairo2-dev libpng12-dev libossp-uuid-dev
sudo apt-get install libfreerdp-dev libpango1.0-dev libssh2-1-dev libtelnet-dev 
sudo apt-get install libvncserver-dev libpulse-dev libssl-dev libvorbis-dev
sudo apt-get install autoconf

sudo wget http://jaist.dl.sourceforge.net/project/guacamole/current/source/guacamole-server-0.9.3.tar.gz
sudo tar -zxvf guacamole-server-0.9.3.tar.gz
sudo cd guacamole-server-0.9.3/
sudo autoreconf -fi
sudo ./configure --with-init-dir=/etc/init.d
sudo make
sudo make install
sudo ldconfig
sudo /etc/init.d/guacd start
```
###setup guacamole-client
Download guacamole-client war package ,and deploy the `guacamole.war` into tomcat7 
```
wget http://jaist.dl.sourceforge.net/project/guacamole/current/binary/guacamole-0.9.3.war
mv guacamole-0.9.3.war /var/lib/tomcat7/webapps/guacamole.war
```


###config guacamole
Check the guacamole config file `/etc/guacamole/guacamole.properties`, and edit the file like this:
```shell
guacd-hostname: localhost
guacd-port:     4822

lib-directory: /var/lib/guacamole
auth-provider: com.openhackathon.guacamole.OpenHackathonAuthenticationProvider
auth-request-url: http://localhost:15000/api/guacamoleconfig
```
Then copy the auth-provider jar file to the path that was setted in the config file
```
sudo cp deploy/openhackathon-gucamole-authentication-1.0-SNAPSHOT.jar /var/lib/guacamole/
```
Note: the `auth-request-url` value must be setted match the _open-hackathon_ src provides
And every time you change this file , you may need to restart guacd and tomcat7 service

#config tomcat7
After installed tomcat7 we need to make tomcat load the guacamole-UI web application. The guacamole.war was provided after we install guacamole commponent.     
So we can config tomcat7 like these steps:
```
sudo mkdir /usr/share/tomcat7/.guacamole
sudo ln -s /etc/guacamole/guacamole.properties /usr/share/tomcat7/.guacamole/guacamole.properties

sudo service guacd restart
sudo service tomcat7 restart
```

#Deploy open-hackathon withn uWsgi

Before deploy the web application ,we need to setup all the dependencies and do some pre-execution
```
echo "127.0.0.1    hackathon.chinacloudapp.cn" >> /etc/hosts
sudo mkdir /var/log/uwsgi
sudo mkdir /var/log/open-hackathon
cd /opt/open-hackathon
virtualenv venv
source venv/bin/activate
cd /opt/open-hackathon/open-hackathon/
sudo pip install -r requirement.txt
```
####- confi mysql
edit `/etc/mysql/my.conf` make changes like this:
```shell
[client]
default-character-set=utf8

[mysqld]
default-storage-engine=INNODB
character-set-server=utf8
collation-server=utf8_general_ci
```
Then restart the `mysqld` service     

Next logon mysql console with root user(mysql -u root -p) and then:
```mysql
create database hackathon;
create User 'hackathon'@'localhost' IDENTIFIED by 'hackathon';
GRANT ALL on hackathon.* TO 'hackathon'@'localhost';
```
Next update `app/config.py` with your user/password. And don't submit your password to github!!!

Then we should initialize tables and creat test data:
```
sudo python /opt/open-hackathon/open-hackathon/src/setup_db.py
mysql -u root -p
use hackathon;
insert into register (register_name, email, enabled) values("Your Name", "xxx@abc.com", 1);
```
####- deploy withn nginx
To deploy the web application in nginx service , we need to provide:            
- a conf file to let nginx load it; 
- a uWsgi to hold the python-flask web application;    - 

To make it to be easily operational, we would setup a linux demo to hanld the uwsgi process           

What we need is already putted in the `deploy` folder, So we can do it like this:
```
sudo rm -rf /etc/nginx/sites-enabled/default
sudo cp deploy/nginx_openhackathon.conf /etc/nginx/conf.d/
sudo cp deploy/nginx_openhackathon.uwsgi.ini ./
sudo cp deploy/uwsgi /etc/init.d/
```
Note: Please check the three files carefully , especially about the paths !!!           
Then we would start and restart these services
```
sudo /etc/init.d/guacd restart
sudo /etc/init.d/tomcat7 restart
sudo /etc/init.d/uwsgi start
```
# Test the Web-application
After finishsd those steps you could do some tests on local machine                     
check guacd service:[http://localhost:8080/guacamole](http://localhost:8080/guacamole)                            
check nginx service for proxy forwarding:[http://hackathon.chinacloudapp.cn/guacamole](http://localhost:8080/guacamole)           
check open-hackathon web application:[http://localhost](http://localhost:8080/guacamole)                   


#Python IDE
Get "PyCharm" from [https://www.jetbrains.com/pycharm/](https://www.jetbrains.com/pycharm/) freely on your localhost     
Extract the download `pycharm-community-4.0.4.tar.gz` , execuse `pycharm-community-4.0.4/bin/pycharm.sh`can open this software.
Then we can develop or debug the open-hackathon

# setup cloudVM service

####download dependencies 
```
sudo apt-get install docker.io
sudo pip install -r /opt/open-hackathon/cloudvm/requestment.txt
```
####download docker images 
```
sudo docker pull 42.159.103.213:5000/rails
sudo docker pull 42.159.103.213:5000/mean
```
after pull down these two images PLS rename to `msopentechcn/rails` and `msopentechcn/mean` withn this commnad:      
`sudo docke images` to find out imageID from image name              
`sudo docker tag <imageID> "newName"`   to rename image     
Then pull down other three images                      
```
sudo docker pull msopentechcn/flask
sudo docker pull rastasheep/ubuntu-sshd
sudo docker pull sffamily/ubuntu-gnome-vnc-eclipse
```
####config docker remote api
If you want to use docker remote api to visit docker on your host machine or Azure server, please change the following configure:          
Please edit this file: /etc/init/docker.conf or /etc/default/docker and update the DOCKER_OPTS variable to the following:
```
DOCKER_OPTS = '-H tcp://0.0.0.0:4243 -H unix:///var/run/docker.sock'
```
The daemon process will listen on port '4243', if '4243' port has been occupied on the machine which you want to visit, please change it. 
And add user into docker gourp 
```
sudo groupadd docker
sudo gpasswd -a ${USER} docker
```
Then restart the docker process: `service docker.io restart`

#Debug the web application
