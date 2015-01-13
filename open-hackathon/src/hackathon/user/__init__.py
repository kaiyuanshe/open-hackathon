import sys

sys.path.append("..")
from hackathon.database.models import *
from hackathon.database import db_adapter
from hackathon.log import log
from hackathon.constants import ADMIN


class UserManager(object):
    def __init__(self, db_adapter):
        self.db_adapter = db_adapter

    def get_registration_by_email(self, email):
        return self.db_adapter.find_first_object(Register, email=email, enabled=1)

    def get_all_registration(self):
        return self.db_adapter.find_all_objects(Register, enabled=1)

    def check_first_user(self, user):
        # make the first login user be the first super admin
        admin = self.db_adapter.find_first_object(Role, name=ADMIN)
        if admin.users.count() == 0:
            log.info("no admin found, will let the first login user be the first admin.")
            first_admin = UserRole(admin, user)
            self.db_adapter.add_object(UserRole, first_admin)
            self.db_adapter.commit()


user_manager = UserManager(db_adapter)