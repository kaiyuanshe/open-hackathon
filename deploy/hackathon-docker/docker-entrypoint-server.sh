#!/bin/sh

gunicorn -w 5 -b 0.0.0.0:15000 manager:app