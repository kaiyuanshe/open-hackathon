__author__ = 'Junbo Wang'
__version__ = '2.0'

from flask import Flask
from flask_restful import Api

# flask
app = Flask(__name__)
api = Api(app)
from . import views
