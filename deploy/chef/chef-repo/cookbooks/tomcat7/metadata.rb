name             'tomcat7'
maintainer       'Stephen Carman'
maintainer_email 'scarman@coldlight.com'
license          'Apache 2.0'
description      'Installs/Configures Tomcat'
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version          '0.1.2'

supports "redhat"
supports "centos"
supports "amazon"
supports "fedora"

depends "java"
