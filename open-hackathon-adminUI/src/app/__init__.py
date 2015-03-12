from flask import Flask
from app.functions import safe_get_config


# flask
app = Flask(__name__)

from . import views

app.config["SQLALCHEMY_DATABASE_URI"] = safe_get_config("mysql.connection", "mysql://root:root@localhost/hackathon")
app.config['SECRET_KEY'] = '*K&ep_me^se(ret_!@#$:secret'