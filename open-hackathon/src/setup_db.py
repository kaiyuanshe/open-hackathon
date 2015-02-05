from hackathon.database.models import Role, db
from hackathon.constants import ROLE

def setup_db():
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


    add_role(ROLE.ADMIN)
    add_role(ROLE.HOST)


setup_db()