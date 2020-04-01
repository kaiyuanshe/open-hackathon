#!/bin/sh

python /opt/open-hackathon/open-hackathon-server/src/manager.py init_db
python /opt/open-hackathon/open-hackathon-server/src/manager.py runserver
