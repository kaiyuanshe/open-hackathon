#!/bin/bash

#####  APP specific variables  #######
DOCKER_USER=kaiyuanshe
IMAGE_NAME=guacamole
IMAGE_TAG=latest
######################################

var=$(docker images|grep pynginx/pynginx)

if [ ! -n "$var" ];then
   echo "you don't have the base image, will pull manaul."
   if [[ "$1" == "us" ]] ;then
     echo "image will pull from hub.docker.com !"
   else
	 docker pull registry.cn-hangzhou.aliyuncs.com/pynginx/pynginx
	 docker tag registry.cn-hangzhou.aliyuncs.com/pynginx/pynginx:latest pynginx/pynginx:latest
   fi
else
   echo "you have the image"
fi

echo "Building docker image = ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
docker build -f Dockerfile -t ${DOCKER_USER}/${IMAGE_NAME}':'${IMAGE_TAG} .

echo "Generated docker image = ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
