# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------

__author__ = 'Junbo Wang'
__version__ = '2.0'

from flask import Flask
from hackathon.functions import safe_get_config, get_class
from flask_restful import Api
from flask_cors import CORS

# flask
app = Flask(__name__)
app.config['SECRET_KEY'] = safe_get_config("app.secret_key", "secret_key")

# flask restful
api = Api(app)

# CORS
app.config['CORS_HEADERS'] = 'Content-Type, token, hackathon_id, hackathon_name'
cors = CORS(app)

docker_class = "hackathon.docker.hosted_docker.HostedDockerFormation"
docker = get_class(docker_class)()

from views import init_routes

init_routes()
### example of scheduler
# from scheduler import scheduler
# from datetime import timedelta
# from hackathon.functions import get_now
#
# def alarm(time):
# print('Alarm! This alarm was scheduled at %s.' % time)
# return {
# "key": "val"
# }
#
# alarm_time = get_now() + timedelta(seconds=10)
# scheduler.add_job(alarm, 'date', run_date=alarm_time, args=[datetime.now()])
