import os,sys
sys.path.append(os.getcwd()+'/backend/')
import constants
import orm.tables

os.system('apt-get -y install mysql-server python-mysqldb')
if constants.database_port!=None:
    mysql_cmd = 'mysql -h'+constants.database_url +' -P' + str(constants.database_port)+' -u'+constants.database_username + ' -p'+constants.database_password
else:
    mysql_cmd = 'mysql -h'+constants.database_url +' -u'+constants.database_username + ' -p'+constants.database_password
print mysql_cmd

create_database = 'create database IF NOT EXISTS '+constants.database_database
cmd = 'echo '+create_database +' | ' + mysql_cmd
print cmd
os.system('echo '+create_database +'|' + mysql_cmd)
orm.tables.create_tables(constants.database_str, False)