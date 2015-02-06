from flask import Flask
from flask_restful import Api

# flask
app = Flask(__name__)
from . import views
