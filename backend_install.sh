#!/bin/bash

#notice: if you failed to install these packages, try to figure it out by changing the source list.

apt-get update
apt-get -y install build-essential



# install curl and pip

apt-get -y install curl

curl https://bootstrap.pypa.io/get-pip.py | sudo python



# web.py installation

wget http://webpy.org/static/web.py-0.37.tar.gz

tar -xvf web.py-0.37.tar.gz

cd web.py-0.37

python setup.py install

cd ..

rm -rf web.py-0.37*



# mysql installation

apt-get -y install mysql-server mysql-client python-mysqldb


# azure installation, modify the __init__.py is needed

pip install azure



# sqlalchemy installation

pip install sqlalchemy



# wsgilog installation

wget https://pypi.python.org/packages/source/w/wsgilog/wsgilog-0.3.tar.gz

tar -xvzf wsgilog-0.3.tar.gz

cd wsgilog-0.3

python setup.py install

cd ..

rm -rf wsgilog-0.3*
