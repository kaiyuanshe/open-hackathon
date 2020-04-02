#!/bin/sh

gunicorn -w 1 -b 0.0.0.0:15000 manager:app