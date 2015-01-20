import sys

sys.path.append("..")
from hackathon.database.models import *
from hackathon.database import db_adapter
from hackathon.log import log
from datetime import datetime, timedelta
from hackathon.constants import ROLE
from hackathon.functions import safe_get_config
from flask_login import logout_user, login_user
import uuid


class UserManager(object):
    def __init__(self, db_adapter):
        self.db = db_adapter

    def __check_first_user(self, user):
        # make the first login user be the first super admin
        admin = self.db.find_first_object(Role, name=ROLE.ADMIN)
        if admin.users.count() == 0:
            log.info("no admin found, will let the first login user be the first admin.")
            first_admin = UserRole(admin, user)
            self.db.add_object(first_admin)
            self.db.commit()

    def __generate_api_token(self, user):
        token_issue_date = datetime.utcnow()
        token_expire_date = token_issue_date + timedelta(
            minutes=safe_get_config("login/token_expiration_minutes", 1440))
        user_token = UserToken(str(uuid.uuid1()), user, token_expire_date, token_issue_date)
        self.db.add_object(user_token)
        self.db.commit()
        return user_token

    def __validate_token(self, token):
        t = self.db.find_first_object(UserToken, token=token)
        if token is not None and token.expire_date >= datetime.utcnow():
            return t.user
        return None

    def get_registration_by_email(self, email):
        return self.db.find_first_object(Register, email=email, enabled=1)

    def get_all_registration(self):
        reg_list = self.db.find_all_objects(Register, enabled=1)

        def online(r):
            u = self.db.find_first_object(User, email=r.email)
            if u is not None:
                r.online = u.online
            else:
                r.online = 0
            return r

        map(lambda r: online(r), reg_list)
        return reg_list

    def logout(self, user):
        try:
            self.db.update_object(user, online=0)
            self.db.commit()
        except Exception as e:
            log.error(e)
            
        logout_user()

    def login(self, openid, **kwargs):
        # update db
        user = self.db.find_first_object(User, openid=openid)
        if user is not None:
            self.db.update_object(user,
                                  name=kwargs["name"],
                                  nickname=kwargs["nickname"],
                                  email=kwargs["email"],
                                  access_token=kwargs["access_token"],
                                  avatar_url=kwargs["avatar_url"],
                                  last_login_time=datetime.utcnow(),
                                  online=1)
            self.db.commit()
        else:

            user = User(name=kwargs["name"],
                        nickname=kwargs["nickname"],
                        email=kwargs["email"],
                        access_token=kwargs["access_token"],
                        avatar_url=kwargs["avatar_url"],
                        last_login_time=datetime.utcnow(),
                        online=1)
            self.db.add_object(user)
            self.db.commit()

        # login flask
        login_user(user)
        log.info("user login successfully:" + repr(user))

        # make the first login user be admin
        self.__check_first_user(user)

        # generate API token
        token = self.__generate_api_token(user)
        return {
            "token": token,
            "user": user
        }

    def validate_token(self, token):
        return self.__validate_token(token)


user_manager = UserManager(db_adapter)