__author__ = 'juniwang'

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)

from app import server