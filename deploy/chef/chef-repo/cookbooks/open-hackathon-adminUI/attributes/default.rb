default['open-hackathon-adminUI']['HOSTNAME'] = 'http://hack-admin-dev.chinacloudapp.cn'
default['open-hackathon-adminUI']['QQ_OAUTH_STATE'] = 'openhackathon'
default['open-hackathon-adminUI']['HACKATHON_API_ENDPOINT'] = 'http://open-hackathon.chinacloudapp.cn:15002'
default['open-hackathon-adminUI']['environment'] = 'local'

default['open-hackathon-adminUI']['github']['client_id'] = '0f0e47f99e682730b68e' 
default['open-hackathon-adminUI']['github']['client_secret'] = 'ce1e4aa7f879a560e77b796b423789126b962cee'
default['open-hackathon-adminUI']['github']['scope'] = 'user'

default['open-hackathon-adminUI']['qq']['client_id'] = '101200890'
default['open-hackathon-adminUI']['qq']['client_secret'] = '88ad67bd4521c4cc47136854781cb9b5'
default['open-hackathon-adminUI']['qq']['scope'] = 'get_user_info'
default['open-hackathon-adminUI']['qq']['response_type'] = 'code'
default['open-hackathon-adminUI']['qq']['grant_type'] = 'authorization_code'
default['open-hackathon-adminUI']['qq']['meta_content'] = '274307566465013314076545663016134754100636'

default['open-hackathon-adminUI']['gitcafe']['client_id'] = '1c33ecdf4dd0826325f60a92e91834522b1cdf47a7f90bdaa79f0526fdc48727'
default['open-hackathon-adminUI']['gitcafe']['client_secret'] = '80b63609000b20c1260df28081c08712617648e1b528086bbb089f0af4614509'
default['open-hackathon-adminUI']['gitcafe']['response_type'] = 'code'
default['open-hackathon-adminUI']['gitcafe']['scope'] = 'public'
default['open-hackathon-adminUI']['gitcafe']['grant_type'] = 'authorization_code'

default['open-hackathon-adminUI']['hackathon']['name'] = 'open-xml-sdk'

default['open-hackathon-adminUI']['provider'] ='["github","qq"]'
default['open-hackathon-adminUI']['session_minutes'] = '60'
default['open-hackathon-adminUI']['token_expiration_minutes'] = '60*24'

default['open-hackathon-adminUI']['weibo']['meta_content'] = 'ae884e09bc02b700'
default['open-hackathon-adminUI']['weibo']['client_id'] = '1943560862'
default['open-hackathon-adminUI']['weibo']['client_secret'] = 'a5332c39c129902e561bff5e4bcc5982'
default['open-hackathon-adminUI']['weibo']['grant_type'] = 'authorization_code'
default['open-hackathon-adminUI']['weibo']['scope'] = 'all'

default['open-hackathon-adminUI']['git']['repository'] = 'git@github.com:msopentechcn/open-hackathon.git'
default['open-hackathon-adminUI']['git']['revision'] = 'master'

default['open-hackathon-adminUI']['app']['secret_key'] = 'secret_key'

default['open-hackathon-adminUI']['mysql']['user'] = 'zgq'
default['open-hackathon-adminUI']['mysql']['password'] = 'zgq'
default['open-hackathon-adminUI']['mysql']['hostname'] = '139.217.129.174'
default['open-hackathon-adminUI']['mysql']['db'] = 'hackathon'
default['open-hackathon-adminUI']['mysql']['port'] = '3306'

default['open-hackathon-adminUI']['git']['repository'] = 'git@github.com:msopentechcn/open-hackathon.git'
default['open-hackathon-adminUI']['git']['revision'] = 'master'

default['open-hackathon-adminUI']['sys_user'] = 'openhackathon'

default['open-hackathon-api']['root-dir'] = '/opt/open-hackathon'

default['open-hackathon-api']['uwsgi']['base'] = '/opt/open-hackathon/open-hackathon/src'
default['open-hackathon-api']['uwsgi']['pythonpath'] = '/opt/open-hackathon/open-hackathon/src'
default['open-hackathon-api']['uwsgi']['http-port'] = '80'
default['open-hackathon-api']['uwsgi']['logto-dir'] = '/var/log/uwsgi'
default['open-hackathon-api']['uwsgi']['hacka-logto-dir'] = '/var/log/open-hackathon'
default['open-hackathon-api']['uwsgi']['logto'] = '/var/log/uwsgi/%n.log'


