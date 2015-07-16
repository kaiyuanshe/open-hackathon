
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

| Keywords        | Interpretation          |
|:--------:|:-----------------------------------------------------------------------------:|
| template  | as a description of the Docker container|
| experiment | correspond with a Docker container|
| team | every user must join in a team to participate in hackathon event|

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
[Imgur](http://i.imgur.com/TZgnKvN.png?1)
`create hackathon`: name and display name    
[Imgur](http://i.imgur.com/40e0WKT.png)
`organizer`：include organizer description  
[Imgur](http://i.imgur.com/Nt72XiY.png)
`event images`: upload event images to show your hackathon event 
[Imgur](http://i.imgur.com/JRPIP1K.png)
`hackathon basic info`: hackathon event basic info setup  
[Imgur](http://i.imgur.com/1qp26bI.png)

### Manage basic info
## Manage registration
## Manage administrators
## Manage Azure certificate
## Manage templates
## Manage experiment


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
`tools/docker-enter`: tool to quickly connect to a running docker container              
                  
                   
 Use Flask to build the whole project.[Flask Introduction](http://flask.pocoo.org/docs/0.10/)
 
 
 
## Try openhackathon quickly
    介绍如何用doker的一个image来run起一个openhackathon
## Setup develop environment
### Setup Docker Env
介绍下docker在OpenHackathon的作用         
[Docker intsallation on Ubuntu](https://docs.docker.com/installation/ubuntulinux/)
    
### Setup Guacamole Env
Guacamole is used as a remote client to connect to running environments , SSH RDP VNC are all provided. [Guacamole](http://guac-dev.org/) can give you more details.        
                 
[Guacamole installation](http://guac-dev.org/doc/gug/installing-guacamole.html)

Gucamole has its own authentication so does OpenHackathon, in order to unify them we customise a new auth provider and hacked it into guacamole client
    
### Setup MysqlDB Env
### Setup Python Env
Find out the `requirement.txt` both in `open-hackathon-server` and `open-hackathon-client` in src folders, all dependencies are recorded in , we can install them through a simply command :   
```
sudo pip install -r open-hackathon-server/requirement.txt
sudo pip install -r open-hackathon-client/requirement.txt
```

config-sample =》config

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






