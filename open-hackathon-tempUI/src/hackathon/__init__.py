__author__ = 'Junbo Wang'
__version__ = '2.0'

from flask import Flask

# flask
app = Flask(__name__)

from . import views
