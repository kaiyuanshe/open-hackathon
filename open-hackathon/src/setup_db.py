from hackathon.database.models import Role, db
from hackathon.constants import ROLE

def setup_db():
    # initialize db tables
    # make sure database and user correctly created in mysql
    # in case upgrade the table structure, the origin table need be dropped firstly
    db.create_all()

setup_db()