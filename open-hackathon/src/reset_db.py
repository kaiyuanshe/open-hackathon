from hackathon.database.models import db
from setup_db import setup_db

db.drop_all()
setup_db()
