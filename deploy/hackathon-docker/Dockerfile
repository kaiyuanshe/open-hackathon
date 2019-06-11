# -*- coding: utf-8 -*-
#
# This file is covered by the LICENSING file in the root of this project.
#

### Dockerfile for open-hacnathon(server and client)
### based on python official image

FROM python:2.7

USER root

#logs
RUN mkdir -p /var/log/open-hackathon/
# server
RUN mkdir -p /opt/open-hackathon/open-hackathon-server
ADD ./open-hackathon-server /opt/open-hackathon/open-hackathon-server
#client
RUN mkdir -p /opt/open-hackathon/open-hackathon-client
ADD ./open-hackathon-client /opt/open-hackathon/open-hackathon-client
#init
ADD ./deploy/hackathon-docker/docker-entrypoint.sh /opt/open-hackathon

RUN pip install -r /opt/open-hackathon/open-hackathon-server/requirements.txt
RUN pip install -r /opt/open-hackathon/open-hackathon-client/requirements.txt

ENTRYPOINT ./opt/open-hackathon/docker-entrypoint.sh
