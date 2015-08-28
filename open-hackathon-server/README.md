Open Hackathon Platform API service
=============================

<!-- toc -->
* [Getting Started](#getting-started)
* [Setup](#setup)
  * [Install MySQL](#install-mysql)
  * [Install docker](#install-docker)
  * [Clone SourceCode](#clone-sourcecode)
  * [Setup Guacamole](#setup-guacamole)
  * [Install Pathon and Python modules](#install-pathon-and-python-modules)
  * [Configure MySQL](#configure-mysql)
  * [Run](#run)
  * [Debug](#debug)
* [API](#api)
  * [Experiment](#experiment)


<!-- toc stop -->

# Getting Started
This document will tell you how to setup your local development environment for open-hackathon API service as well as the API list.

# Setup

This guide show you how to setup your local development environment quickly.

### Install MySQL
```
sudo apt-get update
sudo apt-get install mysql-server libmysqlclient-dev
```

### Install docker
Follow [docker installation guide](https://docs.docker.com/installation/ubuntulinux/) to install docker. You can choose install the latest version of docker. But we strongly recommend you to
 install a stable version since docker itself is developing and updating. Usually lasted version has unexpected issues.

after docker installed, you can try pulling down some docker images:
```
sudo docker pull sffamily/ubuntu-gnome-vnc-eclipse
sudo docker pull rastasheep/ubuntu-sshd
sudo docker pull hall/guacamole
```

##### enable docker remote api
###### Ubuntu 15.04
Make sure docker remote api enabled. As [Official Docs](https://docs.docker.com/articles/systemd) said, the best way is to update `systemd` in the newer versions of docker.
Open file `/lib/systemd/system/docker.service` for editing and change line starting with `ExecStart` to following:
```
ExecStart=/usr/bin/docker daemon -H tcp://0.0.0.0:4243 -H unix:///var/run/docker.sock
```
Change `4243` to other port on demand. And then run `systemctl reload` in shell to reload the new configuration. And restart docker by `service docker restart`.

Now, brower to `http://localhost:4243/_ping`. A simple `OK` shown indicates the remote API is working now. 
Browse to `http://localhost:4243/containers/json` to see the information of running containers. 
For more API, please refer to [Docker remote API Docs](https://docs.docker.com/reference/api/docker_remote_api/)

###### Ubuntu 14.10 and lower
On an old version of Ubuntu, you can edit one of the following files:`/etc/default/docker` or `/etc/init.d/docker`. 
Add new line `DOCKER_OPTS='-H tcp://0.0.0.0:4243 -H unix:///var/run/docker.sock'` and then restart docker by `sudo service docker restart`

##### run docker without sudo(Optional)
And add user into docker group so that you can run docker commands without sudo
```
sudo groupadd docker
sudo gpasswd -a ${USER} docker
```
Relogin USER and restart the docker process: `sudo service docker restart`

##### enable docker-enter(Optional)
After you pull down the source codes, copy `<SRC_ROOT>/tools/docker-enter/docker-enter` and `<SRC_ROOT>/tools/docker-enter/nsenter` to `/usr/local/bin`. 
It's for simplicity that you enter a running docker container. A simple command `sudo docker-enter $(container ID)` help you enter the container.
See `<SRC_ROOT>/tools/docker-enter/usage.txt` for more information.

### Clone SourceCode

first of all, make sure `git` installed. Please follow the [Git installation guide](http://git-scm.com/book/en/v2/Getting-Started-Installing-Git) in case it's not ready.
And then clone source code from github to your local system. Any local folder is OK, we will clone to `/opt` in this document. However you
can change it to any directory you want.
```
cd /opt/
git clone https://github.com/msopentechcn/open-hackathon.git
```

**_Notice that you MUST [folk](http://www.worldhello.net/gotgithub/04-work-with-others/010-fork-and-pull.html) the repository to your account/organization before contributing any changes. Pull Requests are welcome._**

### Setup Guacamole
for simplicity, we recommend you start guacamole using `docker`.
```
sudo docker run -d -i -t -p 8080:8080 -v /opt/open-hackathon/deploy/guacamole:/etc/guacamole hall/guacamole
```
change the port and directory if needed. Also make sure `guacamole.properties` file is correctly configured. The file is in
<<<<<<< HEAD
directory `/opt/open-hackathon/deploy/guacamole` and it's right for you local environment by default. The content may look like:
```
# Hostname and port of guacamole proxy
guacd-hostname: localhost
guacd-port:     4822

lib-directory: /etc/guacamole

# Auth provider class (authenticates user/pass combination, needed if using the provided login screen)
auth-provider: com.openhackathon.guacamole.OpenHackathonAuthenticationProvider
auth-request-url: http://osslab.msopentech.cn:15000/api/guacamoleconfig
```
Usually the only config need to update is `auth-request-url`. _You need to stop the guacamole container and start another one
in case `guacamole.properties` updated_.
directory `/opt/open-hackathon/deploy/guacamole` and it's right for you local environment by default. Usually the only config need to update is `auth-request-url`.
_You need to stop the guacamole container and start another one in case `guacamole.properties` updated_.

##### install guacamole manually(not via docker)
in case you want to install guacamole locally rather than docker , refer to [instrutions](https://github.com/msopentechcn/open-hackathon/wiki/Setup-Guacamole-withn-custom-authentication) for the detailed steps.

### Install Pathon and Python modules
download [Python 2.7](https://www.python.org/downloads/) and add script `python` to your `$PATH`. Make sure the version of python is 2.7.
python 3.* may be supported but we didn't test it.
And install required libs:
```
sudo apt-get install python-dev python-setuptools
sudo easy_install pip
cd /opt/open-hackathon/
sudo pip install -r open-hackathon/requirement.txt
```

### Configure MySQL
Make sure the MySQL is using `utf-8` charset. Edit `/etc/mysql/my.conf` make changes like this:
```
[client]
default-character-set=utf8

[mysqld]
default-storage-engine=INNODB
character-set-server=utf8
collation-server=utf8_general_ci
```
Then restart the `mysqld` service by `service mysqld restart`

Next logon mysql console with root user(`mysql -u root -p`) and then:
```mysql
create database hackathon;
create User 'hackathon'@'localhost' IDENTIFIED by 'hackathon';
GRANT ALL on hackathon.* TO 'hackathon'@'localhost';
```
Next update `app/config.py` with your user/password. And don't submit your password to github!!!

Then we should initialize tables and creat test data:
```
sudo python /opt/open-hackathon/open-hackathon/src/setup_db.py
sudo python /opt/open-hackathon/open-hackathon/src/create_test_data.py
```
### Run
then make sure log folder is created and properly authorized.
```
sudo mkdir /var/log/open-hackathon
sudo chmod -R 644 /var/log/open-hackathon
```

one last step, create your own config file by coping the config-sample.py and editing its content:
```
cd /opt/open-hackathon/open-hackathon/src/hackathon
cp config-sample.py config
```
usually, you need update the guacamole config or DB configs.

Everything is OK now! Start the API server in command line:
```
cd /opt/open-hackathon/open-hackathon/src
sudo python run.py
```
open your brower and navigate to the health page, by default it should be http://localhost:15000

if the status shown is "OK", everything is done.

### Debug
We recommend you install [PyCharm Community Version](https://www.jetbrains.com/pycharm/download/) to debug our code. Of course you can
choose other IDE but you need to figure out how to debug by yourself.
make sure `debug` mode is set `True` in file `/opt/open-hackathon/open-hackathon/src/run.py`. Start PyCharm and:
- open your project
- and click`Run -> Edit Configuration`
- add an new `python` configuration. Fill the required blanks and Apply
- click Debug Icon(a spider icon) in toolbar to start debugging

# API
See [API wiki](https://github.com/msopentechcn/open-hackathon/wiki/Open-hackathon-Restful-API) for details of the RestAPI exposed.

-------------------------------
&copy;2015 Microsoft Open Technologies, Inc. All Rights Reserveds
