# -*- coding: utf-8 -*-
#
# This file is covered by the LICENSING file in the root of this project.
#

### Dockerfile for open-hacnathon(server)
### based on python official image

FROM python:2.7

USER root

#logs
RUN mkdir -p /var/log/open-hackathon/
# server
RUN mkdir -p /opt/open-hackathon/open-hackathon-server
ADD ./open-hackathon-server /opt/open-hackathon/open-hackathon-server
#config
RUN cp /opt/open-hackathon/open-hackathon-server/src/hackathon/config_docker.py /opt/open-hackathon/open-hackathon-server/src/hackathon/config.py
#init
ADD ./deploy/hackathon-docker/docker-entrypoint-server.sh /opt/open-hackathon

RUN pip install -r /opt/open-hackathon/open-hackathon-server/requirements.txt

ENTRYPOINT ./opt/open-hackathon/docker-entrypoint-server.sh
