
<h1 align = "center">OpenHackathon Manual</h1>   
<p align = "center">Microsot Open Technologies</p>                  
<p align = "center">Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd. All rights reserved</p>
.

* [Introduction](#introduction)
  * [What is OpenHackathon](#what-is-openhackathon)
  * [Why OpenHackathon](#why-openhackathon)
* [User's Guide](#user's-guide)
  * [Quick Guide](#implementation-and-architecture-for-user)
    
    Open Hackathon doesn’t have user management service, user and administrator need use social login to log into Open Hackathon.

    For User:
      *  Register: On Open Hackathon main page, user will see all available hackathons. Choose any one will direct user to social login, then user will ask to fulfill some basic information.
      *  Enroll: Choose a hackathon and click enroll. After hackathon administrators approve your request, you will able to attend the hackathon
      *  Team: User can create or attend a team to co-operate with others. Team will share same Git project and same environment.
      *  Submit: User can submit  project for judgers to review.
      
    For Administrator:
    
      *  Management: Admins can create and manage hackathon. Including basic info, register time, competition time, review time and more settings.
      
    For All:
    
      *  Template: Template is a pre-configured environment that anyone can contribute, and used to specific hackathon on our Template library.

    

  * [attend hackathons](#how-to-attend-a-hackathon)
  * [Contribute your Template](#contribute-your-template)
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
    
     Open Hackathon is a clientless, plugin free platform. The following pic shows structure.

     ![Imgur]

     Open Hackathon doesn't have user register service, all users need social login before access any functions. You need config this before you can use social login. Open-hackathon software will manage Azure resource that you provide to create hackathon environment for users. Guacamole is used to display VM in user's web browser, and MySQL server records all necessary data.

     * HTML5 Browser

      Open Hackathon is a clientless web access software, you don’t have to install any
      client software or plugin for browser. Instead,  any browser which can support HTM5 can be used
      to access Open Hackathon. 

     * Open-Hackathon

      Open-Hackathon is main part of Open Hackathon Project. It’s only can be
      install on Linux, provide user interface and admin’s management portal.

     * MySQL

      MySQL is usedas our Database. It was the world's second most  widely used RDBMS, and the most widely used open-source RDBMS.

     * Guacamole

      Guacamole is a clientless remote desktop gateway. It supports standard protocols like VNC
and RDP.  It’s used to connect virtual machine and present it to user via HTML5 based browser.

     * Azure

      Microsoft Azure is used as our base infrastructure. All environment and virtual machines
are built on it.

     * Docker
     
      Docker containers wrap up a piece of software in a complete file system that contains everything it needs to run: code, runtime, system tools, system libraries – anything you can install on a server. This guarantees that it will always run the same, regardless of the environment it is running in.
     
  * [Try OpenHackathon quickly](#try-openhackathon-quickly)
  * [Setup develop environment](#setup-develop-environment)
    * [Setup Docker Env](#setup-docker-env)
    * [Setup Guacamole Env](#setup-guacamole-env)
    * [Setup MysqlDB Env](#setup-mysqlDB-env)
    * [Setup python Env](#setup-python-env)
  * [Config file](#config-file)
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
## Contribute your Template
### Create Template 
进入创建模板页面
填写模板表单数据。

>带星号的都为必填项。
>每个模板可以添加多个image(单元)，而每个image可以添加多个端口号。

### Upload Template
进入上传模板页面。
提供默认模板文件下载。
上传模板文件。

默认template文件格式，可以在原有的基础上进行修改。
``` json
{
    "name": "test-template-1",
    "display_name":"test template 1"
    "description" : "a template consists of a list of virtual environments, and a virtual environment is a virtual machine with its storage account, container, cloud service and deployment",
    "virtual_environments": [
        {
            "provider": "docker", 
            "name": "vnc",
            "image": "42.159.103.213:5000/mono",
            "ports":[{
                "name": "website",
                "port": 80,
                "public": true
            },{
                "name": "Dev",
                "port": 5901,
                "public": true
            }],
            "AttachStdin":false,
            "AttachStdout":true,
            "AttachStderr":true,
            "tty": true,
            "stdin_open": true,
            "remote": {
                "provider": "guacamole",
                "protocol": "vnc",
                "username": "root",
                "password": "acoman",
                "port": 5901
            }
        }
    ]
}
```
**Description**

* `"name"` required , string : There are not special characters
* `"display_name"` string :
* `"description"` string :
* `"virtual_environments"` array: There must be a virtual_environment
  *  `"provider"` "docker"  | "azure":
  *  `"name"` string :
  *  `"image"` url :
  *  `"ports"` array: There must be a port
    *  `"name"`: string:
        *  `"port"`: 0 ~ 65535:
        *  `"public"`: bool:
  *  `"AttachStdin"` bool :    
  *  `"AttachStdout"` bool :
    *  `"AttachStderr"` bool :
    *  `"tty"` bool :
    *  `"stdin_open"` bool :
    *  `"remote"`: object
      *  `"provider"` string,
        *  `"protocol"` string,
        *  `"username"` string,
        *  `"password"` string,
        *  `"port"` 0~65535
        
>上传template文件出错，会有相应的提示信息，重新修改模板内容再次上传。

### Manage Template
**下载** 下载template文件。
**测试** 测试template是否能启动环境 。
**更新** 更新template基础信息。

>当添加或者修改模板数据，模板的`'status'`会被设定义为*'untested'*。



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






