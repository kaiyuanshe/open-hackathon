#### What is guacamole?
[Guacamole](http://guac-dev.org/) is a free, open-source and clientless remote desktop gateway.
It supports standard protocols like VNC ,SSH and RDP. Open Hackathon uses it as an option for remote connection.

#### Customized authentication
However, the default authentication providers offered by Guacamole cannot work well with open hackathon platform. 
So we [customized](https://github.com/msopentechcn/open-hackathon/tree/master/openhackathon-guacamole-auth-provider) the 
authentication following the [guacamole mannual](http://guac-dev.org/doc/gug/custom-authentication.html). You can find the detail instructions in [guacamole mannual](http://guac-dev.org/doc/gug/custom-authentication.html) about how to 
deploy customized guacamole authentication provider. 

#### Quick instructioins for OHP
We assume you have installed guacamole server/client already. If not, see [installation guide](http://guac-dev.org/doc/gug/installing-guacamole.html). And see [install and configure guacamole](https://github.com/msopentechcn/open-hackathon/blob/master/documents/developer_guide.md#install-and-configure-guacamole) for more.
