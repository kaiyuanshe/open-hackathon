LABOSS
======

Open Source Software Laboratory

# Preconditions
- Python 2.7: [download python](https://www.python.org/downloads/)
- pip: [install pip](http://pip.readthedocs.org/en/latest/installing.html)
- mysql: [download mysql](http://dev.mysql.com/downloads/) make sure the character set is correctly set to `utf8`
- install required libs by issue `sudo apt-get install python-dev libmysqlclient-dev`
- *windows only*: [visual c++ compiler for python](http://www.microsoft.com/en-us/download/details.aspx?id=44266)
- *windows only*: [install MySQL Connector/C for windows](http://dev.mysql.com/downloads/connector/c/6.0.html#downloads)
- git:[install git](http://git-scm.com/downloads).
- _optional_, you can install [SmartGit]() if you feel uncomfortable about git bash.
- install PyCharm IDE: [download PyCharm Community](https://www.jetbrains.com/pycharm/download/).
- install Java: `sudo apt-get install openjdk-7-jre`
- docker: [install docker](https://docs.docker.com/installation/). Don't forget to [add your login uesr to docker group](http://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo)

# setup python
after all the preconditions are met on your dev machine, install the required python libraries via pip by:

`pip install -r requirements.txt`.

Note that the file may not up-to-date. When you see error like `no module named XXX`, that means you need install
the specific lib in the error message, try `pip install XXX` in this case.

# setup mysql
configure your mysql instance to add users/privileges. DON'T use root user.

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
and then restart mysql by `/etc/init.d/mysql stop; /etc/init.d/mysql start`.
In case you have created your DB already before set the charset, you can alter the charset of existing database by `ALTER DATABASE mydatabasename charset=utf8;`

next logon mysql console with `root` user(`mysql -u root -p`) and then:

```
create database hackathon;
create User 'hackathon'@'localhost' IDENTIFIED by 'your_password';
GRANT ALL on hackathon.* TO 'hackathon'@'localhost';
```
Next update `app/config.py` with your user/password.  And don't submit your password to github.

## configure logs

```
sudo mkdir /var/log/osslab
sudo chmod 777 /var/log/osslab
```

## initialize tables
run `python src/setup_db.py` for the first time to create db tables;

## add test data

run `sudo python src/create_test_data.py` to add your cloudvm server.(make sure `cloudvm` service started on your local machine, to start
`cloudvm` service see README.md in dir `<src_root>/cloudvm`)

also, you need add your primary email of your github account to `register` table. To query your primary email, browse to [github.com](https://github.com)
click `settings` on the topright corner, then click `emails`. The commands may look like:

```
mysql -u root -p
use hackathon;
insert into register (register_name, email, submitted, enabled) values("Your Name", "xxx@abc.com", 0, 1);
```


# run

## hosts
important that you update your `hosts` file to resolve `osslab.msopentech.cn` to your local ip.
That's because the social login(both github and QQ) requires that the domain name must be `osslab.msopentech.cn`.

Add line `127.0.0.1 osslab.msopentech.cn` to `/etc/hosts` on Unix or `C:\Windows\System32\drivers\etc\hosts` on Windows.

## run
change directory to `osslab/src` and run `python run.py` to start the flask server.

By default the server will listen on port `80` and run in debug model. You can edit run.py to listen a different port.

Browse to `http://localhost` to see the welcome page to make sure its ready.

## notice on windows
you cannot listen on port 80 by default on windows since the windows http service is listening on 80. Try run `net stop http`
on command line to stop http service and release 80 port. Moreover, you may want to run `sc config http start= disabled` to
prevent http service from being started automatically during windows reboot. _After this, you cannot start IIS any more. Start
`http` service if you do need IIS_.
