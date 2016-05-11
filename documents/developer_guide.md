<h1 align="center">Developer Guide</h1>
<p align="center">
<a href="https://github.com/msopentechcn/open-hackathon/blob/master/documents/organizer_guide.md">Pre</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="https://github.com/msopentechcn/open-hackathon/blob/master/documents/README.md">Back to manual</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="https://github.com/msopentechcn/open-hackathon/blob/master/documents/FAQ.md">Next</a>
</p>
========================

On this page:
* [Implementation and Architecture](#implementation-and-architecture)
* [Setup development Environement](#setup-development-environement)
  * [Clone SourceCode](#clone-sourcecode)
  * [Install Python Packages](#install-python-packages)
  * [Install and Configure guacamole](#install-and-configure-guacamole)
  * [Install and Configure Database](#install-and-configure-database)
  * [Install Docker](#install-docker)
  * [Logging && Hosts](#logging--hosts)
  * [Run](#run)
  * [DEBUG](#debug)
* [Deploy](#deploy)
* [Test](#test)
* [API documemt](https://github.com/msopentechcn/open-hackathon/wiki/Open-hackathon-Restful-API)
* [Python doc](#python-doc)
* [DB schema](#db-schema)

## Implementation and Architecture
Open Hackathon is is made up of many parts. The UI(client) application is actually intended to be simple and minimal, with the majority of the gruntwork performed by backend API server.

![index](http://i.imgur.com/EB7K1vP.png)

major parts of Open Hackathon:
- open hackathon client, which is a [Flask](http://flask.pocoo.org/docs/0.10/)-based website,  provides an portal to end users and organizers. Both users and organizers can browse the site via any modern html5-compatible browser. It always talk to open hackathon server via RESTFul APIs. So client is just one example of OHP presentation layer. It can be fully replaced by another UI site with different styles.

- open hackathon server, a resource manager which allows clients to manage hackathon events, hackathon related resources, templates and so on. 

- [guacamole](http://guac-dev.org/) is an open-source html5-based clientless remote client. OHP leverage guacamole to enable client users access to remote VM/docker throw browers. And we provide a [customized authentication provider](https://github.com/msopentechcn/open-hackathon/tree/master/openhackathon-guacamole-auth-provider) to fit OHP.

## Setup Development Environement
This section shows you how to setup local dev environment for both open-hackathon-server and open-hackathon-client.

### Clone SourceCode

First of all, make sure `git` installed. Please follow the [Git installation guide](http://git-scm.com/book/en/v2/Getting-Started-Installing-Git) in case it's not ready.
And then clone source code from github to your local system. Any local folder is OK, we will clone to `/opt` in this document. However you
can change it to any directory you want.
```
cd /opt/
git clone https://github.com/msopentechcn/open-hackathon.git
```

**_Notice that you MUST [folk](http://www.worldhello.net/gotgithub/04-work-with-others/010-fork-and-pull.html) the repository to your account/organization before contributing any changes. Pull Requests are welcome._**

##### Copy configuration files
There some several `config_sample.py` files in open hackathon repo. Please copy them to the same directory and remove `_sample`. Update the content if neccessary.
```
cd /opt/open-hackathon
cp open-hackathon-server/src/hackathon/config_sample.py open-hackathon-server/src/hackathon/config.py
cp open-hackathon-client/src/client/config_sample.py open-hackathon-client/src/client/config.py
```

As a convention, we put default configurations suitable for development environment in `config_sample.py`. And everytime you want to add/update/delete a configuration section, please update `config_sample.py` first.  By contrast, `config.py` can contains whatever customized or private data, they are ignored automatically by git and will **NEVER** be pushed to github.

### Install Python Packages
By default, Pythoon is already included in Ubuntu. Run `python -V` to check your python version. We are currently develeping and running OHP under python 2.7. If python not installed, please [download Python 2.7](https://www.python.org/downloads/) and add script `python` to your `$PATH`. Again, make sure the version of python is 2.7. python 3.* may be supported but we didn't test it.

And install required libs:
```
sudo apt-get install python-dev python-setuptools
sudo easy_install pip
cd /opt/open-hackathon/
sudo pip install -r open-hackathon-server/requirement.txt
sudo pip install -r open-hackathon-client/requirement.txt
```


### Install and Configure guacamole

Firstly please [download](http://guac-dev.org/release/release-notes-0-9-9) guacamole-server-0.9.9.tar.gz, and then [install](http://guac-dev.org/doc/gug/installing-guacamole.html) guacamole server 0.9.9 firstly. Make sure all protocols including VNC, RDP, ssh and telnet are properly installed.

Since open hackathon has [customized guacamole authentication provider](https://github.com/msopentechcn/open-hackathon/tree/master/openhackathon-guacamole-auth-provider), we need additional steps for it:

```
sudo mkdir /usr/share/tomcat7/.guacamole
sudo mkdir /etc/guacamole
cd /opt/open-hackathon/deploy/guacamole
cp guacamole-sample.properties /etc/guacamole/guacamole.properties
cp *.jar /etc/guacamole
sudo ln -s /etc/guacamole/guacamole.properties /usr/share/tomcat7/.guacamole/guacamole.properties
```

Then [download] (http://guac-dev.org/release/release-notes-0-9-9) guacamole-0.9.9.war, and then copy it to /var/lib/tomcat7/webapps/guacamole.war:
```
cp guacamole-0.9.9.war /var/lib/tomcat7/webapps/guacamole.war
sudo service guacd restart
sudo service tomcat7 restart
```

By default you don't need to change `/etc/guacamole/guacamole.properties` on your local machine. And usually the only config need to update is `auth-request-url` if your open-hackathon-server listens on a different port other than `15000`. _You need to restart tomcat7 and guacd service if `guacamole.properties` updated_.


[Click](http://guac-dev.org/doc/gug/custom-authentication.html) for more about custom authentication.


### Install and Configure Database

1. install MongoDB following [MongoDB installation guide](https://docs.mongodb.org/v3.0/tutorial/install-mongodb-on-ubuntu/) for ubuntu.
Navigate to [MongoDB installation](https://docs.mongodb.org/v3.0/installation/) if are running open hackathon on other OS.

2. Make sure mongodb correctly installed.  You can run `sudo service mongod status` to see the running service. Or issue command `mongo` to try mongodb command line.

3. Init required data by:
Update DB connection parameters in `open-hackathon-server/src/hackathon/config_sample.py` if required(For example you run mongodb on a port other than the default
`27017`). And then setup DB by:
```
sudo python open-hackathon-server/src/setup_db.py
```

You can run `sudo python open-hackathon-server/src/reset_db.py` to re-create all tables. But remember, the existing data will be erased while reset the database.


### Install Docker
Follow [docker installation guide](https://docs.docker.com/installation/ubuntulinux/) to install docker. You can choose install the latest version of docker. But we strongly recommend you to
 install a stable version since docker itself is developing and updating. Usually lasted version has unexpected issues.

after docker installed, you can try pulling down some docker images:
```
sudo docker pull rastasheep/ubuntu-sshd
```

##### enable docker remote api
###### Ubuntu 15.04
Make sure docker remote api enabled. As [Official Docs](https://docs.docker.com/articles/systemd) said, the best way is to update `systemd` in the newer versions of docker.
Open file `/lib/systemd/system/docker.service` for editing and change line starting with `ExecStart` to following:
```
ExecStart=/usr/bin/docker daemon -H tcp://0.0.0.0:4243 -H unix:///var/run/docker.sock
```
Change `4243` to other port on demand. And then run `systemctl daemon-reload` in shell to reload the new configuration. And restart docker by `service docker restart`.

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
See `https://github.com/msopentechcn/open-hackathon/tree/master/tools/docker-enter` for more information.

### Logging && Hosts
Make sure log folder is created and properly authorized. By default it's `/var/log/openhackathon`. You can update the logging path in `open-hackathon-server/src/hackathon/logging.conf` and `open-hackathon-client/src/client/logging.conf`.
```
sudo mkdir /var/log/open-hackathon
sudo chmod -R 644 /var/log/open-hackathon
```

And also, please adding row `127.0.0.1 open-hackathon-dev.chinacloudapp.cn` to your local `/etc/hosts`. That's because most oauth login providers doest't accept domain `localhost` and the default oauth parameters in `config_sample.py` are binded to domain `open-hackathon-dev.chinacloudapp.cn`

### Run
Everything is OK now! Start the open hackathon in command line:
```
cd /opt/open-hackathon
sudo python open-hackathon-server/src/run.py
sudo python open-hackathon-client/src/run.py
```
open your browser and try browsing pages:
- open hackathon server health page: http://open-hackathon-dev.chinacloudapp.cn:15000. The output is json-like and  status should be OK
- open hackathon client: http://open-hackathon-dev.chinacloudapp.cn, the entrance of open hackathon web UI
- super admin page: http://open-hackathon-dev.chinacloudapp.cn/admin, a  login page specially for super admin. Default user/pwd is `admin`/`admin`
- guacamole page: http://open-hackathon-dev.chinacloudapp.cn:8080/guacamole. An almost blank page, just tell you guacamole is running

You can start with '发布活动'. More details about [发布活动](https://github.com/msopentechcn/open-hackathon/blob/master/documents/organizer_guide.md)

### Debug
We recommend you install [PyCharm Community Version](https://www.jetbrains.com/pycharm/download/) to debug our code. Of course you can
choose other IDE but you need to figure out how to debug by yourself.
make sure `debug` mode is set `True` in `run.py` files. Start PyCharm and:
- open your project
- and click`Run -> Edit Configuration`
- add an new `python` configuration. Fill the required blanks and Apply
- click Debug Icon(a spider icon) in toolbar to start debugging

## Deploy

To deploy open hackathon to staging or production environment, you need follow all steps of [Setup Development Environment](https://github.com/msopentechcn/open-hackathon/blob/master/documents/developer_guide.md#setup-development-environement) except `Install Docker`, `Run` and `Debug` section. Instead, you should choose one of the python web containers for production usage. For example, [Apache2](http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/#creating-a-wsgi-file), [DotCloud](http://flask.pocoo.org/snippets/48/), [uwsgi](https://uwsgi-docs.readthedocs.org/en/latest/), [gunicorn](http://gunicorn.org/) and so on.

As an example, we show how to deploy open hackathon using `uwsgi` in the following section. However, both `open hackathon platform` and `flask` don't have any limitation on this, choose whatever application you like.

### deploy open hackathon with uwsgi
 **We assume the source codes are cloned to /home/opentech/openhackathon**. If not, please rectify the file path of following files:
```
<src_root>/open-hackathon-server/src/app.wsgi
<src_root>/open-hackathon-server/src/open-hackathon-server.conf
<src_root>/open-hackathon-server/src/open-hackathon-server.ini
<src_root>/open-hackathon-client/src/app.wsgi
<src_root>/open-hackathon-client/src/open-hackathon-client.conf
<src_root>/open-hackathon-client/src/open-hackathon-client.ini
```

- Follow [uwsgi install guide](http://uwsgi-docs.readthedocs.org/en/latest/Install.html) to install uwsgi
- Deploy open hackathon server and client as ubuntu upstart services:
```
sudo cp /home/opentech/open-hackathon/open-hackathon-server/src/open-hackathon-server.conf /etc/init/
sudo service open-hackathon-server start

sudo cp /home/opentech/open-hackathon/open-hackathon-client/src/open-hackathon-client.conf /etc/init/
sudo service open-hackathon-client start
```
- by default, open hackathon server and client listen on port 15000 and 80 respectively. Update the ini file if you want as well as other uwsgi configurations.

### things to know
- You can deploy DB, open hackathon server, open hackathon client to different VM, correct configurations in `config.py` and `/etc/guacamole/guacamole.properties` then if you do so.
- It's getting harder to debug on staging/production environment. One of the most useful tools is logging. By default, logs are in directory `/var/log/open-hackathon` where `open-hackathon-server.log` and `open-hackathon-client.log` are logs for open hackathon API server and UI respectively. Logs for guacamole are `/var/log/syslog` for guacd and `/var/log/tomcat7/*.log` for guacamole client.
- **Very Important**, update `environment` in `config.py` files for both client and server because many features not enabled in default `local` environment. You can change to any value other than `local`.
- And also, review the whole `config.py` files, update values suitable for your environment. For example, oauth key/secrets, DB connections, storage type and configurations.
- By default, Port 80(open hackathon UI), 15000(open hackathon API), 8080(guacamole) should be accessed from public. Which means you have to allow it in your firewall and configure the endpoints in you CloudService(azure), Security group(AWS) and so on.
- By default, the password of super admin, who has the highest privilege and cannot be deleted, is not secure. Don't forgot to update it.
- `Docker` is not required in your server. Actually it's part of resources related to certain hackathon event. So you can install docker on any other VM(even in any other cloud), and then configure it on your hackathon console. See more about [organizer guide](https://github.com/msopentechcn/open-hackathon/blob/master/documents/organizer_guide.md);

## Test
## Python doc
## DB schema
