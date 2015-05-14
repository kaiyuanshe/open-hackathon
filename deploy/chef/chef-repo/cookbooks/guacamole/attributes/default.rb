default['guacamole']['dir'] = '/opt/gua-dir'
default['guacamole']['server-tar'] = 'guacamole-server-0.9.6.tar.gz'
default['guacamole']['server-tar-url'] = "http://jaist.dl.sourceforge.net/project/guacamole/current/source/guacamole-server-0.9.6.tar.gz"
default['guacamole']['client-tar'] = 'guacamole-client-0.9.6.tar.gz'
default['guacamole']['server-tar-extract-dir'] = '/opt/gua-dir/extract'
default['guacamole']['war-path'] = '/var/lib/tomcat7/webapps/guacamole.war'
default['guacamole']['war-url'] = 'http://jaist.dl.sourceforge.net/project/guacamole/current/binary/guacamole-0.9.6.war'
default['guacamole']['war-cookbook-file'] = "guacamole-0.9.6.war"
default['guacamole']['use-local-war'] = 'true'

default['guacamole']['user'] = 'openhackathon'
default['guacamole']['group'] = 'openhackathon'

default['guacamole']['src-folder'] = '/opt/open-hackathon/deploy/guacamole'#'/home/opentech/open-hackathon/deploy/guacamole'#
default['guacamole']['dst-folder'] = '/etc/guacamole'

default['guacamole']['tomcat-guacamole-share-folder'] = '/usr/share/tomcat7/.guacamole'

default['guacamole']['properties'] = 'guacamole.properties'
default['guacamole']['properties-sample'] = 'guacamole-sample.properties'
default['guacamole']['json-jar'] = 'json-20090211.jar'
default['guacamole']['snapshot-jar'] = 'openhackathon-gucamole-authentication-1.0-SNAPSHOT.jar'

default['guacamole']['guacd-hostname'] = 'localhost'
default['guacamole']['guacd-port'] = '4822'
default['guacamole']['lib-directory'] = '/etc/guacamole'
default['guacamole']['auth-provider'] = 'com.openhackathon.guacamole.OpenHackathonAuthenticationProvider'
default['guacamole']['auth-request-url'] = 'http://localhost:15000/api/guacamoleconfig'


