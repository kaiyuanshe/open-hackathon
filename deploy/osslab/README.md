OSSLAB UI

# manual
the manual steps to deploy open-hackathon platform

## install packages

```
sudo apt-get update
sudo apt-get install apache2 git python-pip python-dev mysql-server libmysqlclient-dev libapache2-mod-wsgi
```

## clone source code

```
mkdir -p ~/hackathon/github
cd ~/hackathon/github
git clone https://github.com/msopentechcn/laboss.git
```
## configure mysql
first of all, make sure the character set is correctly set to `utf8`.
```
vim /etc/mysql/my.cnf
```
make changes
```
[client]
default-character-set=utf8

[mysqld]
default-storage-engine=INNODB
character-set-server=utf8
collation-server=utf8_general_ci
```
and then restart mysql by `/etc/init.d/mysql stop; /etc/init.d/mysql start`


logon mysql console via `mysql -u root -p` and then create database/user/access for open hackathon platform.

```
create database hackathon;
create User 'hackathon'@'localhost' IDENTIFIED by 'hackathon';
GRANT ALL on hackathon.* TO 'hackathon'@'localhost';
```
exit mysql console and initialize mysql by:

```
cd /home/opentech/hackathon/github/laboss/osslab/src
sudo python setup_db.py
```

## install python libs

```
cd laboss
sudo pip install -r osslab/requirement.txt
```

## configure logs

```
sudo mkdir /var/log/osslab
sudo chown www-data:www-data /var/log/osslab
```

## configure apache2
update `<src_root>/osslab/osslab.conf` and `<src_root>/osslab/src/app.wsgi` if you clone your code in a different directory other than
the default one(`/home/opentech/hackathon/github/laboss`)

```
sudo cp ./osslab.conf /etc/apache2/sites-available
cd /etc/apache2/sites-enabled
sudo ln -s ../sites-available/osslab.conf osslab.conf
sudo service apache2 restart
```

## update config if needed
in following case, you may want to change config.py:
- the domain of open hackathon site changed. Change the domain in config.py AND change the url in oauth provider sites(qq, github etc)
- the database installed in another server or you configured your own the database user/password

```
vi /home/opentech/hackathon/github/laboss/osslab/src/app/config.py
```
replace the oauth config with correct value.


_Note: if the target directory is changed, update `<src_root>/osslab/src/app.wsgi` and `/etc/apache2/sites-available/osslab.conf` too._