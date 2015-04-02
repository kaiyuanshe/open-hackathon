from flask import Flask
from app.functions import safe_get_config
from flask_debugtoolbar import DebugToolbarExtension


# flask
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = safe_get_config("mysql.connection", "mysql://root:root@localhost/hackathon")
app.config['SECRET_KEY'] = safe_get_config("app.secret_key", "secret_key")

app.config['DEBUG_TB_ENABLED'] = False
toolbar = DebugToolbarExtension(app)

from . import views
