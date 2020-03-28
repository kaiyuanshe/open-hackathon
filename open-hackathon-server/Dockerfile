FROM python:3.7-alpine

LABEL 99kies 1290017556@qq.com https://github.com/99kies

USER root

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    apk update && \
    apk add --no-cache g++ gcc musl-dev libxslt-dev
#logs
RUN mkdir -p /var/log/open-hackathon/
# server
COPY src /src
#config
RUN mv src/hackathon/config_docker.py /src/hackathon/config.py
#init
COPY docker-entrypoint.sh /docker-entrypoint.sh

RUN chmod 777 /docker-entrypoint.sh

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

ENTRYPOINT ./docker-entrypoint.sh
