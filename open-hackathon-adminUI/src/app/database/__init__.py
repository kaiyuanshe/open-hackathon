import sys

sys.path.append("..")
from app.constants import ROLE
from flask_sqlalchemy import SQLAlchemy
from app import app
from db_adapters import SQLAlchemyAdapter

db = SQLAlchemy(app)
db_adapter = SQLAlchemyAdapter(db)


class UserMixin(object):
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_admin_id(self):
        pass

    def get_id(self):
        return unicode(self.get_admin_id())

    def is_admin(self):
        return self.has_roles(ROLE.ADMIN)

