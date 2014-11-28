__author__ = 'Junbo Wang'
__version__ = '2.0'

from flask import Flask
# allen chen 2014/11/24
import os
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID

app = Flask(__name__)
app.config.from_object('config')

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

oid = OpenID()
oid.init_app(app)

from app import views

