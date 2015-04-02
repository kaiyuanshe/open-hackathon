__author__ = 'Junbo Wang'
__version__ = '2.0'

from flask import Flask
from hackathon.functions import safe_get_config
from flask_restful import Api
from flask_cors import CORS

# flask
app = Flask(__name__)
app.config['SECRET_KEY'] = safe_get_config("app.secret_key", "secret_key")

# flask restful
api = Api(app)

# CORS
app.config['CORS_HEADERS'] = 'Content-Type, token'
cors = CORS(app)

from . import views


### example of scheduler
# from scheduler import scheduler
# from datetime import datetime, timedelta
#
# def alarm(time):
# print('Alarm! This alarm was scheduled at %s.' % time)
# return {
#         "key": "val"
#     }
#
# alarm_time = datetime.now() + timedelta(seconds=10)
# scheduler.add_job(alarm, 'date', run_date=alarm_time, args=[datetime.now()])
