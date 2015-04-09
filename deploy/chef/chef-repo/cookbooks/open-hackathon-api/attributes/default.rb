default['open-hackathon-api']['qq']['OAUTH_STATE'] = 'openhackathon'

default['open-hackathon-api']['mysql']['host'] = 'localhost'
default['open-hackathon-api']['mysql']['user'] = 'hackathon'
default['open-hackathon-api']['mysql']['pwd']  = 'hackathon'
default['open-hackathon-api']['mysql']['db']   = 'hackathon'
default['open-hackathon-api']['mysql']['setup-file'] = '/opt/open-hackathon/open-hackathon/src/setup_db.py'

default['open-hackathon-api']['environment'] = 'local'

default['open-hackathon-api']['token_expiration_minutes'] = '60*24'

default['open-hackathon-api']['azure']['subscriptionId'] = '31e6e137-4656-4f88-96fb-4c997b14a644'
default['open-hackathon-api']['azure']['certPath'] = '/home/if/If/LABOSS/open-hackathon/src/hackathon/certificates/1-31e6e137-4656-4f88-96fb-4c997b14a644.pem'
default['open-hackathon-api']['azure']['managementServiceHostBase'] = 'management.core.chinacloudapi.cn'

default['open-hackathon-api']['guacamole']['host'] = 'http://localhost:8080'

default['open-hackathon-api']['scheduler']['job_store'] = 'mysql'

default['open-hackathon-api']['git']['repository'] = 'https://github.com/msopentechcn/open-hackathon.git'
default['open-hackathon-api']['git']['revision'] = 'master'

default['open-hackathon-api']['mysql']['default_storage_engine'] = 'INNODB'
default['open-hackathon-api']['mysql']['collation_server'] = 'utf8_general_ci'
default['open-hackathon-api']['mysql']['initial_root_password'] = 'admin123'
default['open-hackathon-api']['mysql']['version'] = '5.5'
default['open-hackathon-api']['mysql']['port'] = '3310'


default['open-hackathon-api']['user'] = 'openhackathon'
