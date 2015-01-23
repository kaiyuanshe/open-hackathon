import sys
from _codecs import register

sys.path.append("..")
from hackathon.database.models import *
from hackathon.database import db_adapter
from hackathon.log import log
from hackathon.constants import ROLE
from flask_login import logout_user


class UserManager(object):
    def __init__(self, db_adapter):
        self.db_adapter = db_adapter

    def get_registration_by_email(self,emails):
        return self.db_adapter.filter(Register,Register.enabled==1).first()

    def get_all_registration(self):
        reg_list = self.db_adapter.find_all_objects(Register, enabled=1)

        def online(r):
            u = self.db_adapter.find_first_object(User, email=r.email)
            if u is not None:
                r.online = u.online
            else:
                r.online = 0
            return r

        map(lambda r: online(r), reg_list)
        return reg_list

    def check_first_user(self, user):
        # make the first login user be the first super admin
        admin = self.db_adapter.find_first_object(Role, name=ROLE.ADMIN)
        if admin.users.count() == 0:
            log.info("no admin found, will let the first login user be the first admin.")
            first_admin = UserRole(admin, user)
            self.db_adapter.add_object(first_admin)
            self.db_adapter.commit()
            
    def check_email_states(self,emails):
        return self.db_adapter.filter(UserEmail, email in emails)

    def logout(self, user):
        logout_user()
        self.db_adapter.update_object(user, online=0)
        self.db_adapter.commit()


user_manager = UserManager(db_adapter)