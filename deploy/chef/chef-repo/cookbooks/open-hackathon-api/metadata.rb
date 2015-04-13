name             'open-hackathon-api'
maintainer       "Microsoft Open Technologies (Shanghai) Co. Ltd"
maintainer_email "msopentechdevsh@microsoft.com"
license          "MIT"
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
