
<h1 align = "center">OpenHackathon Manual</h1>   
<p align = "center">Microsot Open Technologies</p>                  
<p align = "center">Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd. All rights reserved</p>
.

* [Introduction](#introduction)
  * [What is OpenHackathon](#what-is-openhackathon)
  * [Why OpenHackathon](#why-openhackathon)
* [Keywords and interpretation](#keywords-and-interpretation)
* [User's Guide](#user's-guide)
  * [Implementation and Architecture](#implementation-and-architecture-for-user)
  * [attend hackathons](#how-to-attend-a-hackathon)
  * [Upload Template](#upload-template)
  * [FAQ](#FAQ)
* [Admin's Guid](#admin's-guide)
  * [Implementation and Architecture](#implementation-and-architecture-for-admin)
  * [Manage hackathon](#how-to-manage-a-hackathon)
    * [Create hackathon](#create-hackathon)
    * [Manage basic info](#manage-basic-info)
  * [Manage registration](#manage-registration)
  * [Manage administrators](#manage-administrators)
  * [Manage Azure certificate](#manage-azure-certificate)
  * [Manage templates](#manage-templates)
  * [Manage experiment](#manage-experiment)
  * [FAQ](#FAQ)
* [Developer's Guide](#developer's-guide)
  * [Implementation and Architecture](#implementation-and-architecture-for-developer)
  * [Try OpenHackathon quickly](#try-openhackathon-quickly)
  * [Setup develop environment](#setup-develop-environment)
    * [Setup Docker Env](#setup-docker-env)
    * [Setup Guacamole Env](#setup-guacamole-env)
    * [Setup MysqlDB Env](#setup-mysqlDB-env)
    * [Setup python Env](#setup-python-env)
  * [Customize](#customize)
  * [Test](#test)
    * [Unit test](#unit-test)
    * [API test](#api-test)
  * [API documemt](#api-document)
  * [Python doc](#python-doc)
  * [DB schema](#db-schema)
  * [Contribution.MD](#contribution.md)
  * [FAQ](#QA)




# Introduction
## What is OpenHackathon
## Why OpenHackathon


# Keywords and interpretation

# User's-Guide
## Implementation and Architecture for User
用户角色模块的基础介绍，以及涉及到的各种关键字的解释
### keys 
## How to attend a hackathon
报名，组队，参赛，提交评审等介绍，以及主干流程的截图
## Upload Template
Templat 上传过程及用户对自己上传的Template的管理操作


# Admin's Guide
## Implementation and Architecture for Admin
## Manage Hackathon
### Create hackathon
`Hackathon creation entrance`
![Imgur](http://i.imgur.com/TZgnKvN.png?1)
`create hackathon`: name and display name                  
![Imgur](http://i.imgur.com/40e0WKT.png)
`organizer`：include organizer description                 
![Imgur](http://i.imgur.com/Nt72XiY.png)
`event images`: upload event images to show your hackathon event                 
![Imgur](http://i.imgur.com/JRPIP1K.png)
`hackathon basic info`: hackathon event basic info setup                      
![Imgur](http://i.imgur.com/1qp26bI.png)
`finish creation`:                    
![Imgur](http://i.imgur.com/ZpLUYUJ.png)

### Manage basic info
## Manage registration
The main content of registration managment is auditing all registers 
## Manage administrators
## Manage Azure certificate
## Manage templates
Hackathon administrators can delete or add a template from templates pool to current hackathon
## Manage experiment
Hackathon will provider a runnable environment to every player , naturally the hackathon administrator could manage them , stop or reset them when necessary


#Developer's Guide
## Implementation and Architecture for Developer            
`Project on Github`:`https://github.com/msopentechcn/open-hackathon.git`                         
`Architecture:`                             
OpenHackathon is separated into two pieces: open-hackathon server, which provides the openhackathon proxy and related libraries, and open-hackathon client, which provides the website client to users            

src folders introduction:        
`deploy`: all components for deployment               
`open-hackathon-client`: frontend web project src               
`open-hackathon-server`: backend api server project src              
`openhackathon-guacamole-auth-provider`: guacamole auth provider java project src                 
`tools/docker-enter`: tool to quickly connect to a running docker container through container id             
                  
                   
 Use Flask to build the whole project.[Flask Introduction](http://flask.pocoo.org/docs/0.10/)
 
 
 
## Try openhackathon quickly
    介绍如何用doker的一个image来run起一个openhackathon
## Setup develop environment
To setup the whole OpenHackathon develop environment, you need those components:
```
Docker Service
Guacamole
MysqlDB
Python third part lib
```
### Setup Docker Env
Docker service takes part in OpenHackathon Platform as a environment provider that will provide to all users. And docker service now is the most populer cloudservice, you could get more details on [docker official website](https://www.docker.com/)                         

In OpenHackathon develop evnironment you should install and setup docker service like this: [Docker intsallation on Ubuntu](https://docs.docker.com/installation/ubuntulinux/)                    

In order to control and manage docker service from OpenHackathon conveniently , we'd better to enable docker's `remote API`. Fllow this steps after installation of docker service,[enable docker remote API](http://blog.trifork.com/2013/12/24/docker-from-a-distance-the-remote-api/)
    
### Setup Guacamole Env
Having got many environments we need to find a way to connect them for users, as you know that we choose Guacamole!Guacamole works as a remote client connecting to running environments, which provides SSH, RDP and VNC protocols. So we can cope with various environments of different hackathons        
[Guacamole](http://guac-dev.org/) can give you more details.        


Guacamole installation is separated into two pieces: server and client, service need to be built by src and client can be built to tomcat from a war package directly. More details can follow this:[Guacamole installation](http://guac-dev.org/doc/gug/installing-guacamole.html)             

Note:               
Gucamole has its own authentication so does OpenHackathon, in order to unify them we customise a new auth provider and hacked it into guacamole client. You can use it or you could build a new one.   
To use it you would make the `guacmaole.properties` like this:
```
guacd-hostname: localhost
guacd-port:     4822

lib-directory: /var/lib/guacamole
auth-provider: com.openhackathon.guacamole.OpenHackathonAuthenticationProvider
auth-request-url: http://localhost:15000/api/guacamoleconfig
```
And find the `openhackathon-gucamole-authentication-1.0-SNAPSHOT.jar` in src folders and move it to path that configured in `guacamole.propertied`

If you want to make you own Guacamole auth provider, there is a java project named `openhackathon-guacamole-auth-provider` can give a example, you also can find in out src folders! But, this java project just match `version 0.9.7` of guacamole client!

### Setup MysqlDB Env
First you need to install the components of Mysql and Python libs:
```
sudo apt-get install build-essential python python-dev python-setuptools libmysqlclient-dev
sudo apt-get install mysql-server
```
Then change the ``my.conf` of mysql
```
[client]
default-character-set=utf8

[mysqld]
default-storage-engine=INNODB
character-set-server=utf8
collation-server=utf8_general_ci
```
Then login mysql console with root user(`mysql -u root -p`) and then create develope mysql database like this:
```
create database hackathon;
create User 'hackathon'@'localhost' IDENTIFIED by 'hackathon';
GRANT ALL on hackathon.* TO 'hackathon'@'localhost';
```
Finally please remember match your `config.py` options on mysql configuration


### Setup Python Env
Find out the `requirement.txt` both in `open-hackathon-server` and `open-hackathon-client` in src folders, all dependencies are recorded in , we could install them through a simply command :   
```
sudo pip install -r open-hackathon-server/requirement.txt
sudo pip install -r open-hackathon-client/requirement.txt
```

Then copy a file `config.py` from `config_sample.py`, and modify it as needed. Below is the instruction:


## customize
    如何自定义，
    如何由Azure资源，切换到其他的云服务厂商，如阿里云，盛大云等
    guacamole --> other client provider
    
## Test
### Unit test
### API test
    
## API document
## Python doc
## DB schema
## Contribution.MD






