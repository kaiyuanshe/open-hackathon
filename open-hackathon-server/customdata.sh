#!/bin/sh
LOG=/var/log/vm_docker_log.log
touch $LOG
sudo chmod 777 $LOG
echo 'Start...'>>$LOG
sudo apt-get update -y
echo 'apt-get update'
sudo apt-get install curl -y
echo 'apt-get install curl'>>$LOG
sudo apt-get install sed -y
echo 'apt-get install sed'>>$LOG
sudo apt-get install docker.io -y
res=$?
echo $res>>$LOG 
echo "Docker installation is finished.">>$LOG 
sudo sed -i '$a\DOCKER_OPTS="-H tcp://0.0.0.0:4243 -H unix:///var/run/docker.sock"' /etc/default/docker.io
sudo service docker.io restart 
echo 'done'>>$LOG
