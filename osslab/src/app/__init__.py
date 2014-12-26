__author__ = 'Junbo Wang'
__version__ = '2.0'

from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Keep_me$secret_!!!&'

# disable the debug toolBar and debug mode in production
app.config['DEBUG_TB_ENABLED'] = True
app.debug = True


from app import views

