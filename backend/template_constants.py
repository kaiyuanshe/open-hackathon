'''
Should rename the file to constants.py
'''


'''
Azure SDK Info
'''
SUBSCRIPTION_ID = ''
CERT_FILE = ''
LOCATION=''
LINUX_IMAGE=''
WINDOWS_IMAGE=''
CONTAINER_NAME=''

'''
DB Info
'''
database_url = ''
database_username = ''
database_password = ''
database_port = None #default is 3306
database_database = ''
if database_port!=None:
    database_str = 'mysql+mysqldb://'+database_username+':'+database_password+'@'+database_url+':'+str(database_port)+'/'+database_database+'?charset=utf8'
else:
    database_str = 'mysql+mysqldb://'+database_username+':'+database_password+'@'+database_url+'/'+database_database+'?charset=utf8'

'''
Guacamole Server Info
'''
guacamole_config_path = ''

'''
Log Info already stored in the backendlogger package
'''
log_file = ""#path
log_format = "[%(asctime)s] %(filename)s:%(lineno)d(%(funcName)s): [%(levelname)s] %(message)s"
log_dateformat = "%Y-%m-%d %H:%M:%S"
import logging
log_level = logging.DEBUG
log_interval = "d" 
log_backups = 3


'''
House cleaning time limited
'''
client_time_limit = 7200
server_time_limit = 200