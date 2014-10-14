LABOSS
======

Open Source Software Laboratory

Dependency libs:
web.py
mysql
sqlalchemy
wsgilog
azure python sdk

1. web.py:
	wget http://webpy.org/static/web.py-0.37.tar.gz
	tar -xvzf web.py-0.37.tar.gz
	cd web.py-0.37
	sudo python setup.py install

2. mysql
	sudo apt-get install mysql-client mysql-server

3. sqlalchemy
	pip install sqlalchemy
	pip install python-mysqldb

4. wsgilog
	wget...
	python setup.py install

5. azure python sdk
	cur https://bootstrap.pypa.io/get-pip.py | sudo python
	sudo pip install azure
	For Mooncake, modify the __initII.py for azure in python site-packages,refer to the azure sdk

