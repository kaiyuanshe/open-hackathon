<h1 align="center">Developer Guide</h1>
[Back to manual](https://github.com/msopentechcn/open-hackathon/blob/master/documents/README.md)

On this page:
* [Implementation and Architecture](#implementation-and-architecture)
* [Setup development Environement](#setup-development-environement)

## Implementation and Architecture
Open Hackathon is is made up of many parts. The UI(client) application is actually intended to be simple and minimal, with the majority of the gruntwork performed by backend API server.

![index](http://i.imgur.com/EB7K1vP.png)

major parts of Open Hackathon:
- open hackathon client, which is a [Flask](http://flask.pocoo.org/docs/0.10/)-based website,  provides an portal to end users and organizers. Both users and organizers can browse the site via any modern html5-compatible browser. It always talk to open hackathon server via RESTFul APIs. So client is just one example of OHP presentation layer. It can be fully replaced by another UI site with different styles.

- open hackathon server, a resource manager which allows clients to manage hackathon events, hackathon related resources, templates and so on. 

- [guacamole](http://guac-dev.org/) is an open-source html5-based clientless remote client. OHP leverage guacamole to enable client users access to remote VM/docker throw browers. And we provide a [customized authentication provider](https://github.com/msopentechcn/open-hackathon/tree/master/openhackathon-guacamole-auth-provider) to fit OHP.

## Setup Development Environement
This section shows you how to setup local dev environment for both open-hackathon-serve and open-hackathon-client.
