import sys

sys.path.append("..")
from app.constants import ROLE
from flask_sqlalchemy import SQLAlchemy
from app import app
from db_adapters import SQLAlchemyAdapter
from app.admin.admin_mgr import AdminManager
from flask import g

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

    def check_role(self, role):

        # 0:super admin
        # 1:comman admin

        hackathon_ids = AdminManager.get_hackid_from_adminid(g.admin.id)
        #None  or not None { has -1 or has not }

        if hackathon_ids is None :
            return False
        else:
            #only super admin can access
            if role == [ROLE.SUPER_ADMIN]:
                return (-1L) in (hackathon_ids)
            #comman admin all can access
            else : return True


