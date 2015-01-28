openhackathon-guacamole-auth-provider
==================================
This document is talking about how to setup the Guacamole environment withn custom authentication
Then we can drop the “noauth” and make Guacamole‘s authentication can be controled by our OSSLAB web system;

Steps are as follows:

##Install commponents
After Ubuntu 14.04 LTS finished installation, you should install some components, like these commands:
```
sudo apt-get update
sudo apt-get install vim git maven openssh-server vnc4server
sudo apt-get install libguac-dev libcairo-dev libvncserver0
sudo apt-get install guacamole libguac-client-ssh0 libguac-client-vnc0 
sudo apt-get install tomcat7
sudo apt-get install openjdk-7-jdk
```
Note：    
Never do `apt-get install guacamole-tomcat` !   
Because it would make the connection between tomcat6 and guacd very frail !     
it is better to separate them when install the two commponents !

##build custom authentication project
To build the project you need to check your java and maven environment withn commands like this:
```
java -version
javac -version
mvn -version
```
Check the results wheather the versions are matched


Then download the maven project sourece codes from github withn command:
```
https://github.com/mshubian/openhackathon-guacamole-auth-provider.git
```
build the project withn these steps:
```
cd guacamole-auth-hmac
sudo mvn package
```
and wait until the results like this:
```
[INFO]
[INFO] --- maven-jar-plugin:2.2:jar (default-jar) @ guacamole-auth-hmac ---
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time: 4.027s
[INFO] Finished at: Wed Dec 31 16:50:28 CST 2014
[INFO] Final Memory: 11M/154M
[INFO] ------------------------------------------------------------------------
```
After project build successfully you will find the `openhackathon-gucamole-authentication-1.0-SNAPSHOT.jar` in the `target` folder, this jar file will provide the authentication service

##config guacamole
Check the guacamole config file `/etc/guacamole.properties`, and edit the file like this:
```shell
# Hostname and port of guacamole proxy
guacd-hostname: 42.159.29.99
guacd-port:     4822

lib-directory: /var/lib/guacamole
auth-provider: com.openhackathon.guacamole.OpenHackathonAuthenticationProvider
auth-request-url: http://osslab.msopentech.cn/checkguacookies

```
Note: never left any 'namespace' at ends of every line!        
then copy the maven build out jar file into the property `lib-directory` path;     
```
sudo cp openhackathon-guacamole-auth-provider/target/openhackathon-gucamole-authentication-1.0-SNAPSHOT.jar /var/lib/guacamole
```
#config tomcat7
After install tomcat7 we need to make tomcat load the guacamole web application, we just need to copy the `guacamole.war` to `webapps` and some other necessary operations. And the guacamole.war was provided after we install guacamole commponent.     
So we can config tomcat7 like these steps:
```
sudo ln -s /var/lib/tomcat7/conf /usr/share/tomcat7/conf
sudo ln -s /var/lib/tomcat7/webapps /usr/share/tomcat7/webapps
sudo chmod 777 /usr/share/tomcat7/webapps
sudo cp /var/lib/guacamole/guacamole.war /usr/share/tomcat7/webapps/

sudo mkdir /usr/share/tomcat7/.guacamole
sudo ln -s /etc/guacamole/guacamole.properties /usr/share/tomcat7/.guacamole/guacamole.properties
sudo chmod 777 /usr/share/tomcat7/.guacamole/guacamole.properties

sudo service guacd restart
sudo service tomcat7 restart
```

##Test withn an example
