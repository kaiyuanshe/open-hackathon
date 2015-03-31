__author__ = 'Junbo Wang'
__version__ = '2.0'

from flask import Flask
from flask_restful import Api
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from hackathon.functions import safe_get_config

# flask
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = safe_get_config("app.secret_key", "secret_key")

app.config['DEBUG_TB_ENABLED'] = False
toolbar = DebugToolbarExtension(app)

# flask login
login_manager = LoginManager()
login_manager.login_view = "index"
login_manager.login_message_category = "info"
login_manager.init_app(app)

from . import views
