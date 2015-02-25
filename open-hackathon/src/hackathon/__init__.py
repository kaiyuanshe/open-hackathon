__author__ = 'Junbo Wang'
__version__ = '2.0'

from flask import Flask
from hackathon.functions import safe_get_config
from flask_restful import Api
from flask_cors import CORS

# flask
app = Flask(__name__)
app.config['SECRET_KEY'] = '*K&ep_me^se(ret_!@#$'

# flask restful
api = Api(app)

# CORS
app.config['CORS_HEADERS'] = 'Content-Type, token'
cors = CORS(app)


# db configuration
app.config["SQLALCHEMY_DATABASE_URI"] = safe_get_config("mysql.connection", "mysql://root:root@localhost/hackathon")

from . import views
