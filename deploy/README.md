
<h1 align = "center">OpenHackathon Manual</h1>   
<p align = "center">Microsot Open Technologies</p>                  
<p align = "center">Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd. All rights reserved</p>
.

* [Introduction](#introduction)
  * [What is OpenHackathon](#what-is-openhackathon)
  * [Why OpenHackathon](#why-openhackathon)
* [Glossary](#glossary)
* [User Guide](#user-guide)
  * [Attend Hackathon](#how-to-attend-a-hackathon)
  * [Contribute your Template](#contribute-your-template)
* [Organizer Guide](#organizer-guide)
  * [Manage Hackathon](#manage-hackathon)
    * [Create a new hackathon](#create-hackathon)
    * [Manage hackathon basic info](#manage-hackathon-basic-info)
  * [Manage registered users](#manage-registered-users)
  * [Manage administrators](#manage-administrators)
  * [Manage Azure certificate](#manage-azure-certificate)
  * [Manage templates](#manage-templates)
  * [Manage experiment](#manage-experiment)
* [Developer Guide](#developer-guide)
  * [Implementation and Architecture](#implementation-and-architecture-for-developer)
  * [Try OpenHackathon quickly](#try-openhackathon-quickly)
  * [Setup develop environment](#setup-develop-environment)
    * [Setup Docker](#setup-docker)
    * [Setup Guacamole](#setup-guacamole)
    * [Setup MySQLDB](#setup-mysqldb)
    * [Setup Python](#setup-python)
  * [Config file](#config-file)
  * [Customize](#customize)
  * [Test](#test)
    * [Unit test](#unit-test)
    * [API test](#api-test)
  * [API documemt](#api-document)
  * [Python doc](#python-doc)
  * [DB schema](#db-schema)
  * [Contribution.MD](#contribution.md)
  * [FAQ](#faq)




# Introduction
## What is OpenHackathon
Open Hackathon Platform is a cloud-based platform to enable Hacakthon organizers to host an offline/online hacakthon with most needed features; Hackathon event participants can use a HTML5 capable web browser to login an Hackathon event, provision his development environment of choice and collaborate with teammates.

The Open Hacakthon can be deployed as a standalone web application, and can leverage Docker based technology to efficiently manage the cloud resources.
## Why OpenHackathon
- **Free**. Open Hackathon Platform is an fully open-source under MIT license. 
- **imple**. Participants don't need to install or configure anything. A html5 capable web browser and a social login account are the only preconditions. Nowadays HTML5 is supported in all modern browsers. And Open Hackathon platform supports several major OAuth providers including QQ, weibo, github, gitcafe and microsoft live login. It's easy to support more.
- **Scalable**. Every component of open hackathon platform can be scalable.

# Glossary
- **_OHP_**: abbreviation of Open Hackathon Platform 
- **_Hackathon_**: an online or offline event in which computer programmers and others involved in software development and hardware development, including graphic designers, interface designers and project managers, collaborate intensively on software projects
- **_Template_**: a template defines the configurations of  development environment for hackers including both hardware and software. A template consists of one or more virtual environment, see virtual environment for more.
- **_Virtual Environment_** a virtual environment can be a docker container on linux OS or a windows virtual machine. For docker container, we need to include the image name, exposed ports, login, command and environment variables which are actually parameters for docker remote API. For windows VM,  since we only support Microsoft Azure currently, you should specify the VM image name, OS type, network configurations, storage account, cloud service and deployment and so on. Again, all those configurations are for azure restful API.  A few more words, although we support azure only, it's very easy to support other public cloud such as AWS or Ali cloud.
- **_Experiment_** a running environments which are started according to some template. It consists of running docker containers and/or running virtual machines.
- **_User/Participant_**: those who attend certain hackathon
- **_Administrator_**: those who initiate a hackathon.  Note that one cannot be participant of a hackathon if  he/she is the administrator of that hackathon. But administrator of hackathon A can be user of hackathon B.
- **_Judge_**:  those who can judge the result committed by users. 

# User Guide

## How to attend a hackathon
报名，组队，参赛，提交评审等介绍，以及主干流程的截图
## Contribute your Template
Templat 上传过程及用户对自己上传的Template的管理操作

# Organizer Guide
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

### Manage hackathon basic info
## Manage registered users
The main content of registration managment is auditing all registers 
## Manage administrators
As a administrator of a hackathon , he can manage other admins in the same hackathon . The major operations of admin's managment are:          

**create admin** : add a common user to admin groups only if he has signed in this platform                  
**modify admin** : just make role type exchange from ‘judgment’ and 'common admin'                 
**delete admin** : just remember that : the hackathon owner can not be deleted by anyone !     

The details are as follows:                           
get the `administrator managment` entrance from the admin site home page :             
![Imgur](http://i.imgur.com/z80WsFA.png)
After you get the list of all adminstrators of current hackathon , you can begin your managment on 'administrators'.              

To create a new administrator, click `添加` on the header of the list table :
![Imgur](http://i.imgur.com/iNsvDKY.png)
Fill in the form required , and submit you request. If the user never signed in , you should do this step again after he signed in .                             


To modify admin , click the modify button in `操作`, as mentioned that only the role type of amin can be modifed
![Imgur](http://i.imgur.com/iyOifcU.png)


To delete a admin, click the delete button in `操作`, as mentioned that the owner of the hackathon can not be deleted in any case !
![Imgur](http://i.imgur.com/fTKC7Ii.png)

## Manage Azure certificate
## Manage templates
Hackathon administrators can delete or add a template from templates pool to current hackathon
## Manage experiment
Hackathon will provider a runnable environment to every player , naturally the hackathon administrator could manage them , stop or reset them when necessary


#Developer Guide
## Implementation and Architecture for Developer            
`Project on Github`:`https://github.com/msopentechcn/open-hackathon.git`                         
`Architecture:`                             
OpenHackathon is separated into two pieces: open-hackathon server, which provides the openhackathon proxy and related libraries, and open-hackathon client, which provides the website client to users            

src folders introduction:        
**deploy**: all components for deployment               
**open-hackathon-client**: frontend web project src               
**open-hackathon-server**: backend api server project src              
**openhackathon-guacamole-auth-provider**: guacamole auth provider java project src                 
**tools/docker-enter**: tool to quickly connect to a running docker container through container id             
src framework intriduction：                    
Use `Flask` to build the whole project.[Flask Introduction](http://flask.pocoo.org/docs/0.10/)
 
 
 
## Try openhackathon quickly
    介绍如何用doker的一个image来run起一个openhackathon
## Setup develop environment
To setup the whole OpenHackathon develop environment, you need those components:

**Docker Service**
**Guacamole**
**MysqlDB**
**Python third part lib**

### Setup Docker
Docker service takes part in OpenHackathon Platform as a environment provider that will provide to all users. And docker service now is the most populer cloudservice, you could get more details on [docker official website](https://www.docker.com/)                         

In OpenHackathon develop evnironment you should install and setup docker service like this: [Docker intsallation on Ubuntu](https://docs.docker.com/installation/ubuntulinux/)                    

In order to control and manage docker service from OpenHackathon conveniently , we'd better to enable docker's `remote API`. Fllow this steps after installation of docker service,[enable docker remote API](http://blog.trifork.com/2013/12/24/docker-from-a-distance-the-remote-api/)
    
### Setup Guacamole
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

### Setup MySQLDB
First you need to install the components of Mysql and Python libs:
```
sudo apt-get install build-essential python python-dev python-setuptools libmysqlclient-dev
sudo apt-get install mysql-server
```
Then change the `my.conf` of mysql like this:
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
Please remember match your `config.py` options on mysql configuration , finally execute the `setup_db.py` withn command or other ways , like this:
```
sudo python open-hackathon/open-hackathon-server/src/setup_db.py
```
Now , you can write and design you own OpenHackathon freely !

### Setup Python
Find out the `requirement.txt` both in `open-hackathon-server` and `open-hackathon-client` in src folders, all dependencies are recorded in , we could install them through a simply command :   
```
sudo pip install -r open-hackathon-server/requirement.txt
sudo pip install -r open-hackathon-client/requirement.txt
```

Then copy a file `config.py` from `config_sample.py`, and modify it as needed. Below is the instruction:

##Config file
| Item      |    Value | Qty  |
|:---------:|:--------:| :-----------------------|
| Computer  | 1600 USD |  5   |
| Phone     |   12 USD |  12  |
| Pipe      |    1 USD | 234  |

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
## FAQ
