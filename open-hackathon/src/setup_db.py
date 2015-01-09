from hackathon.database import *
from hackathon.constants import ADMIN, HOST

# initialize db tables
# make sure database and user correctly created in mysql
# in case upgrade the table structure, the origin table need be dropped firstly
db.create_all()


# initialize roles
def add_role(role):
    r = Role.query.filter_by(name=role).first()
    if r is None:
        db.session.add(Role(role))
        db.session.commit()


add_role(ADMIN)
add_role(HOST)
