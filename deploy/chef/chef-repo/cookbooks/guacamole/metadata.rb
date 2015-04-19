name             "guacamole"
maintainer       "Stratus Technologies"
maintainer_email "jeff.dutton@stratus.com"
license          "Apache 2.0"
description      "Installs/Configures guacamole"
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version          IO.read(File.join(File.dirname(__FILE__), 'VERSION')) rescue "0.0.1"

supports "ubuntu"

depends "apt"
depends "tomcat"
