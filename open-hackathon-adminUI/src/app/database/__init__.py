import sys

sys.path.append("..")
from flask_sqlalchemy import SQLAlchemy
from app import app
from db_adapters import SQLAlchemyAdapter

db = SQLAlchemy(app)
db_adapter = SQLAlchemyAdapter(db)

