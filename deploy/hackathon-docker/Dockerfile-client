# -*- coding: utf-8 -*-
#
# This file is covered by the LICENSING file in the root of this project.
#

### Dockerfile for open-hacnathon(client)
### based on python official image

FROM python:2.7

USER root

#logs
RUN mkdir -p /var/log/open-hackathon/
#client
RUN mkdir -p /opt/open-hackathon/open-hackathon-client
ADD ./open-hackathon-client /opt/open-hackathon/open-hackathon-client
#config
RUN cp /opt/open-hackathon/open-hackathon-client/src/client/config_docker.py /opt/open-hackathon/open-hackathon-client/src/client/config.py
#init
ADD ./deploy/hackathon-docker/docker-entrypoint-client.sh /opt/open-hackathon

RUN pip install -r /opt/open-hackathon/open-hackathon-client/requirements.txt

ENTRYPOINT ./opt/open-hackathon/docker-entrypoint-client.sh
