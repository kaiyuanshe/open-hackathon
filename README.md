LABOSS
======

Open Source Software Laboratory

Dependency libs:
web.py
mysql
sqlalchemy
wsgilog
azure python sdk

1. web.py
	i.   wget http://webpy.org/static/web.py-0.37.tar.gz
	ii.  tar -xvzf web.py-0.37.tar.gz
	iii. cd web.py-0.37
	iv.  sudo python setup.py install

2. mysql
	i. sudo apt-get install mysql-client mysql-server

3. sqlalchemy
	i.  pip install sqlalchemy
	ii. pip install python-mysqldb

4. wsgilog
	i.  wget...
	ii. python setup.py install

5. azure python sdk
	i.   cur https://bootstrap.pypa.io/get-pip.py | sudo python
	ii.  sudo pip install azure
	iii. For Mooncake, modify the __initII.py for azure in python site-packages,refer to the azure sdk

