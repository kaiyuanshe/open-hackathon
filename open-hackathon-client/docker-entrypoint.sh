#!/bin/sh

cd /src
gunicorn -w 5 -b 0.0.0.0:80 run:app
# Five processes started