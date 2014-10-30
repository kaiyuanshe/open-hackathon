OSSLab
======
Open Source Software Laboratory
step1: update
sudo apt-get update

step2: install flask

download virtualenv.py，https://raw.githubusercontent.com/pypa/virtualenv/master/virtualenv.py

sudo apt-get install python-virtualenv

install pip:

wget get-pip，https://bootstrap.pypa.io/get-pip.py

flask/bin/pip install flask==0.9
flask/bin/pip install flask-login
flask/bin/pip install flask-openid
flask/bin/pip install flask-mail
flask/bin/pip install sqlalchemy==0.7.9
flask/bin/pip install flask-sqlalchemy==0.16
flask/bin/pip install sqlalchemy-migrate
flask/bin/pip install flask-whooshalchemy==0.54a
flask/bin/pip install flask-wtf
flask/bin/pip install pytz==2013b
flask/bin/pip install flask-babel==0.8
flask/bin/pip install flup

step3 : install SQLAlchemy and Mysql
http://www.keakon.net/2012/12/03/SQLAlchemy%E4%BD%BF%E7%94%A8%E7%BB%8F%E9%AA%8C

step4: install apache2 and deploy the flask on the apache2
sudo apt-get install apache2
http://blog.163.com/sywxf_backup/blog/static/21151212520128202312687/
sites-enabled/000-default.conf
modify the config files
the port 80 should be opened.
