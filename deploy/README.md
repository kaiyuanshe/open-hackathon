
<h1 align = "center">OpenHackathon Manual</h1>   
<p align = "center">Microsot Open Technologies</p>                  
<p align = "center">Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd. All rights reserved</p>
.

* [Introduction](#introduction)
  * [What is OpenHackathon](#what-is-openhackathon)
  * [Why OpenHackathon](#why-openhackathon)
* [User's Guide](#user's-guide)
  * [Implementation and Architecture](#implementation-and-architecture-for-user)
User use a HTML5 based browser connect to Open Hackathon.  After third-part login, user will see
hackathon main page, after hackathon owner approved user’s request, user will
able to choose an environment to start, hackathon will start environment on
Microsoft Azure and display it on user’s web browser.
**HTML5 Browser**
Open Hackathon is a clientless web access software, you don’t have to install any
client software or plugin for browser. Instead,  any browser which can support HTM5 can be used
to access Open Hackathon.
**Open-Hackathon**
Open-Hackathon is main part of Open Hackathon Project. It’s only can be
install on Linux, provide user interface and admin’s management portal.
**MySQL**
MySQL is usedas our Database. It was the world's second most  widely used RDBMS, and the most widely used open-source RDBMS.
**Guacamole**
Guacamole is a clientless remote desktop gateway. It supports standard protocols like VNC
and RDP.  It’s used to connect virtual machine and present it to user via HTML5 based browser.
**Azure**
Microsoft Azure is used as our base infrastructure. All environment and virtual machines
are built on it.
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
In this part, you will learn how to change your Hackathon's basic information after completing creation. First of all, click *Edit Hackathon* directly if you want to edit current Hackathon.

![Imgur](http://i.imgur.com/UFN4911.png)

>**Attention:**If you want to edit other Hackathon, please change current Hackathon or go to the page of *Hackathon Management* and click the *Management* button in the status column of the Hackathon which you would like to change, as showing below.

![Imgur](http://i.imgur.com/Cx2ki8h.png)

Then, you will go to the following basic information page, which looks like the page you came to when creating a Hackathon.

![Imgur](http://i.imgur.com/e6vY0AX.png)

In this page, you can edit or change all basic information about your Hackathon, including Hackathon display name, activity location, number of members, several time settings and Hackathon description. You can also choose whether to use  [Alauda](http://www.alauda.cn/) and free registration.

- **Hackathon display name:** the name to be displayed on the web page
- **Activity location:**the location of Hackathon
- **Number of members:**the maximum number of members
- **Activity time:**the start time and the end time of activity
- **Registration time:**the start time and the end time of registration
- **Judgement time:**the start time and the end time of judgement
- **Whether to use Alauda:**whether to use Alauda container
- **Whether to use free registration:**whether to allow user register freely or after audit
- **Activity introduction:**some detailed descriptions about this Hackathon

Besides, in the top right corner, you can select the status of this Hackathon,  containing *Online, Offline or Draft*.

![Imgur](http://i.imgur.com/sGqcCbW.png)

>**Attention:**Once you select **Online** mode, this Hackathon will appear on the home page and can be available to anyone.

At last, you can upload extra images by clicking *Activity Pictures* button in the top right corner. And then you go to the  *Upload* page to upload your images.

![Imgur](http://i.imgur.com/2qgvJD3.png)

##Manage registration
In this part, you will learn how to audit registers.

>**Attention:**If your Hackathon does not need audit, users can register freely and join in the activity directly.

![Imgur](http://i.imgur.com/G0rz1Ql.png)

As the administrator of Hackathon, you should go the *User Management* page, as shown below, where you can check the basic information of every register, including name, team, telephone number, address, status and operation. All you need to do is selecting a status, *approve or reject*, for the register.

![Imgur](http://i.imgur.com/lX62VGv.png)

![Imgur](http://i.imgur.com/Sn7vp1E.png)
![Imgur](http://i.imgur.com/ppaj2Bv.png) 
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


#Developer's Guide
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
 
 
 
##Try openhackathon quickly

 In this part, you will learn how to DIY (*Deploy It Yourself*) your openhackathon application with the help of docker.
 >**Attention：**To begin with this part, you should have [Docker](https://www.docker.com/) pre-installed and get familar with it.

### 1 Get the image for openhackathon
We have had our openhackathon image built and push it to [Docker Hub](https://hub.docker.com/account/signup/). You can download this image by running `docker pull image_tag` command, where the image_tag is "`42.159.103.213:5000/ohid_0.1`". 
```bash
sudo docker pull 42.159.103.213:5000/ohid_0.1
```
>**Note1：**To avoid permission problem, please run as **root**.

>**Note2：**The size of openhackathon image is about 2.4GB, so you need pretty time and patience to download it if your network environment is not satisfying.

### 2 Launch docker container
Now you can launch a container with `docker run` command, after successfully download the image. We expose four tcp posts as listed below. Please make sure the map of these ports is correct.
<table>
	<thead>
		<tr>
		 <th>Application</th>
		 <th>Inner port</th>
		 <th>Outer port</th>
		</tr>
	</thead>
	<tbody>
	<tr>
		<td>open-hackathon-ui</td>
		<td>80</td>
		<td>N/A</td>
	</tr>
	<tr>
		<td>open-hackathon-client</td>
		<td>8000</td>
		<td>N/A</td>
	</tr>
	<tr>
		<td>open-hackathon-server</td>
		<td>15000</td>
		<td>N/A</td>
	</tr>
	<tr>
		<td>tomcat/guacamole</td>
		<td>8080</td>
		<td>N/A</td>
	</tr>
	</tbody>
</table>
To launch the container, you can input the command in your terminal, as written below.
```bash
sudo docker run -i -t -p 80:80 -p 8000:8000 -p 8080:8080 -p 15000:15000 image_tag
```
>**Tip:**For more details about parameters, please refer to [docker userguide](http://docs.docker.com/userguide/dockerimages/).

>**Attention:**Before running this command, you should make sure **outer ports** haven't been used by other applications.


### 3 Configure your environment for openhackathon
Due to the mechanism of the  third-party OAuth, you need *full domain name* and **80** port to guarantee the running of openhackathon application. We have set **hackathon.contoso.com** as our hostname. All you need to do is mapping this domain name to the IP address **127.0.0.1**. To accomplish this, you should run the following command in your terminal.
```bash
sudo echo "127.0.0.1 hackathon.contoso.com">>/etc/hosts
```

### 4 Congratulations!
Now start your browser, type in *`hackathon.contoso.com`* in your address bar, press the *Enter* button and enjoy your openhackathon application.

## Setup develop environment
To setup the whole OpenHackathon develop environment, you need those components:

**Docker Service**
**Guacamole**
**MysqlDB**
**Python third part lib**

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

### Setup Python Env
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






