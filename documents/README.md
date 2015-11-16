
<h1 align = "center">OpenHackathon Manual</h1>
<p align = "center">Microsot Open Technology Center</p>
<p align = "center">[Contact us](mailto:msopentechdevsh@microsoft.com)</p>
<p align = "center">Copyright (c) 2015 Microsoft</p>



* [Introduction](#introduction)
  * [What is OpenHackathon](#what-is-openhackathon)
  * [Why OpenHackathon](#why-openhackathon)
* [Glossary](#glossary)
* [User Guide](https://github.com/msopentechcn/open-hackathon/wiki/%E5%BC%80%E6%94%BE%E9%BB%91%E5%AE%A2%E6%9D%BE%E5%B9%B3%E5%8F%B0%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97)
* [Organizer Guide](#organizer-guide)
  * [Create a new hackathon](#create-hackathon)
  * [Edit hackathon basic info](#manage-hackathon-basic-info)
  * [Manage registered users](#manage-registered-users)
  * [Manage administrators and judges](#manage-administrators)
  * [Manage organizers](#manage-organizers)
  * [Manage awards](#manage-awards)
  * [Manage Azure certificate](#manage-azure-certificate)
  * [Manage templates](#manage-templates)
  * [Manage experiment](#manage-experiment)
* [Developer Guide](#developer-guide)
  * [Implementation and Architecture](#implementation-and-architecture-for-developer)
  * [Try OpenHackathon quickly](#try-openhackathon-quickly)
  * [Setup develop environment](#setup-develop-environment)
  * [Test](#test)
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

# Organizer Guide
To be done

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
## Setup develop environment
## customize
## Test
## API document
## Python doc
## DB schema
## Contribution.MD
## FAQ
