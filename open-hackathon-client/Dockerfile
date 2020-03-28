FROM python:3.7-alpine

LABEL 99kies 1290017556@qq.com https://github.com/99kies

USER root

COPY requirements.txt /requirements.txt

RUN pip install -r requirements.txt

COPY src /src

RUN mv /src/client/config_docker.py /src/client/config.py

COPY docker-entrypoint.sh /docker-entrypoint.sh

RUN chmod 777 /docker-entrypoint.sh

RUN mkdir -p /var/log/open-hackathon/

EXPOSE 80

ENTRYPOINT ./docker-entrypoint.sh
