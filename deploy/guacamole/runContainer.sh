#!/bin/bash  

#####  APP specific variables  #######
SERVICE_DOCKER_USER=kaiyuanshe
SERVICE_IMAGE_NAME=guacamole
SERVICE_IMAGE_TAG=latest
SERVICE_CONTAINER_NAME=kaiyuanshe-guacamole
SERVICE_CONTAINER_PORT=8080
SERVICE_HOST_BIND_PORT=15000

DAEMON_DOCKER_USER=guacamole
DAEMON_IMAGE_NAME=guacd
DAEMON_IMAGE_TAG=latest
DAEMON_CONTAINER_NAME=kaiyuanshe-guacd
######################################

echo "running containers:"
docker ps
echo ""

echo "stop and remove existing container below:"
docker rm -f ${SERVICE_CONTAINER_NAME}
docker rm -f ${DAEMON_CONTAINER_NAME}

echo ""
echo "port mapping:"
echo "host:container = "${SERVICE_HOST_BIND_PORT}":"${SERVICE_CONTAINER_PORT}
echo ""

docker run --name ${DAEMON_CONTAINER_NAME} -d ${DAEMON_DOCKER_USER}/${DAEMON_IMAGE_NAME}':'${DAEMON_IMAGE_TAG}
docker run -p ${SERVICE_HOST_BIND_PORT}:${SERVICE_CONTAINER_PORT} --link ${DAEMON_CONTAINER_NAME}:${DAEMON_IMAGE_NAME} --name ${SERVICE_CONTAINER_NAME} -d ${SERVICE_DOCKER_USER}/${SERVICE_IMAGE_NAME}':'${SERVICE_IMAGE_TAG}
