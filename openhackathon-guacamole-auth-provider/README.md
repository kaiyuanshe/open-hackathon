openhackathon-guacamole-auth-provider
==================================

## What's openhackathon-guacamole-auth-provider?
Following [custom authentication guide](http://guac-dev.org/doc/gug/custom-authentication.html), we have our implementation here. The major authentication flow for open hackathon is(Assume user logined in, registered on certain hackathon and successfully launched his/her experiment environment):

- when user enter `/workspace` page, client requests the URIs of the experiment where each URI is in fact the address of guacamole client followed by an unique name of an virtual environment. An experiment may contain one or more virtual environments so there might be an array of URI and each has a unique name.
- client append a token to each URI and try to load it in iframe.
- then guacamole client receives the request and begin to authenticate. Just at this time, our customized authentication provider is called.
- inside our implementaion, we call open hackathon server API to get the connection parameters using the token and unique name. Connection parameters include host, port, username, password and so on.
- guacamole client talks to guacamole server and try to connect to remote environment through the connection parameters and present to end users.

## how to build?
This project is java based so make sure you have installed `java` and `maven` properly:
```
java -version
mvn -version
```
We build with `JDK 7`(minor version doesn't matter) and `maven 3`

Simply build this project by:
```
git clone https://github.com/msopentechcn/open-hackathon.git
cd openhackathon-guacamole-auth-provider
mvn verify
```

After project build successfully you will find the `openhackathon-gucamole-authentication-1.0-SNAPSHOT.jar` in the `target` folder, this jar file will provide the authentication service.

**_important_**

We have already include the jar file in `deploy/guacamole` folder, so if only want to use it rather than contribute codes, making use of this jar file directly is the best choice. [How to install and configure guacamole for OHP?](https://github.com/msopentechcn/open-hackathon/blob/master/documents/developer_guide.md#install-and-configure-guacamole)
