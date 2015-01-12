__author__ = 'Junbo Wang'
__version__ = '2.0'

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from hackathon.functions import safe_get_config


app = Flask(__name__)
app.config['SECRET_KEY'] = '*K&ep_me^se(ret_!@#$'

# disable the debug toolBar and debug mode in production
app.config['DEBUG_TB_ENABLED'] = False
app.debug = True
toolbar = DebugToolbarExtension(app)

# db initialization
app.config["SQLALCHEMY_DATABASE_URI"] = safe_get_config("mysql/connection", "mysql://root:root@localhost/hackathon")

# sub modules initialization
from user import UserManager
from expr.expr_mgr import ExprManager

user_manager = UserManager()
expr_manager = ExprManager()

from . import views
