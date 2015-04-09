name             'open-hackathon-api'
maintainer       'Microsoft Open Technologies'
maintainer_email 't-guzho@microsoft.com'
license          'All rights reserved'
description      'Installs/Configures back-end'
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version          '0.1.0'



depends  'apt'
depends  'python'
depends  'uwsgi'
depends  'git'
depends  'mysql','~> 6.0.20'
depends  'postgresql'
depends  'database'
depends  'mysql2_chef_gem'
