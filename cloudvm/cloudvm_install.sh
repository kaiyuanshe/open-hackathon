#!/bin/bash

#notice: if you failed to install these packages, try to figure it out by changing the source list.

apt-get update
apt-get -y install build-essential




# web.py installation

wget http://webpy.org/static/web.py-0.37.tar.gz

tar -xvf web.py-0.37.tar.gz

cd web.py-0.37

python setup.py install

cd ..

rm -rf web.py-0.37*


