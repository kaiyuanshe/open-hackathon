__author__ = 'Junbo Wang'
__version__ = '2.0'

from flask import Flask
#from flask_debugtoolbar import DebugToolbarExtension
from hackathon.functions import safe_get_config
from flask_login import LoginManager
from flask_restful import Api

# flask
app = Flask(__name__)
app.config['SECRET_KEY'] = '*K&ep_me^se(ret_!@#$'

# flask login
login_manager = LoginManager()
login_manager.login_view = "index"
login_manager.login_message_category = "info"
login_manager.init_app(app)

# flask restful
api = Api(app)

# debug toolbar
# disable the debug toolBar and debug mode in production
app.config['DEBUG_TB_ENABLED'] = False
app.debug = True
#toolbar = DebugToolbarExtension(app)

# db configuration
app.config["SQLALCHEMY_DATABASE_URI"] = safe_get_config("mysql/connection", "mysql://root:root@localhost/hackathon")

from . import views
import admin
