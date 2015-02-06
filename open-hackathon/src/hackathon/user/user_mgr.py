import sys

sys.path.append("..")
from hackathon.database.models import *
from hackathon.log import log
from hackathon.database import db_adapter
from datetime import datetime, timedelta
from hackathon.constants import ROLE, HTTP_HEADER
from hackathon.enum import ExprStatus, EmailStatus
from hackathon.functions import safe_get_config
from hackathon.hack import hack_manager
from flask import request, g
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
        if t is not None and t.expire_date >= datetime.utcnow():
            return t.user
        return None

    def __validate_user_registered(self, user, hack):
        emails = map(lambda x: x.email, user.emails.all())
        return self.db.filter(Register, Register.email.in_(emails),
                              Register.enabled == 1,
                              Register.hackathon_id == hack.id).first()

    def get_all_registration(self):
        reg_list = self.db.find_all_objects(Register, enabled=1)

        def online(r):
            u = self.db.find_first_object(UserEmail, email=r.email)
            if u is not None:
                r.online = u.user.online
            else:
                r.online = 0
            return r

        map(lambda r: online(r), reg_list)
        return reg_list

    def db_logout(self, user):
        try:
            self.db.update_object(user, online=0)
            self.db.commit()
            return "OK"
        except Exception as e:
            log.error(e)
            return "log out failed"

    def db_login(self, openid, **kwargs):
        # update db
        email_info = kwargs['email_info']
        user = self.db.find_first_object(User, openid=openid)
        if user is not None:
            self.db.update_object(user,
                                  name=kwargs["name"],
                                  nickname=kwargs["nickname"],
                                  access_token=kwargs["access_token"],
                                  avatar_url=kwargs["avatar_url"],
                                  last_login_time=datetime.utcnow(),
                                  online=1)
            for n in range(0, len(email_info)):
                email = email_info[n]['email']
                primary_email = email_info[n]['primary']
                verified = email_info[n]['verified']
                if self.db.find_first_object(UserEmail, email=email) is None:
                    useremail = UserEmail(name=kwargs['name'], email=email, primary_email=primary_email,
                                          verified=verified, user=user)
                    self.db.add_object(useremail)
            self.db.commit()
        else:
            user = User(openid=openid,
                        name=kwargs["name"],
                        nickname=kwargs["nickname"],
                        access_token=kwargs["access_token"],
                        avatar_url=kwargs["avatar_url"],
                        online=1)

            self.db.add_object(user)
            self.db.commit()

            for n in email_info:
                email = n['email']
                primary_email = n['primary']
                verified = n['verified']
                useremail = UserEmail(name=kwargs['name'], email=email, primary_email=primary_email,
                                      verified=verified, user=user)
                self.db.add_object(useremail)
                self.db.commit()

        # make the first login user be admin
        self.__check_first_user(user)

        # generate API token
        token = self.__generate_api_token(user)
        return {
            "token": token,
            "user": user
        }

    def validate_request(self):
        if HTTP_HEADER.TOKEN in request.headers:
            token = request.headers[HTTP_HEADER.TOKEN]
            user = self.__validate_token(token)
            if user is None:
                return False
            g.user = user
            return True
        return False

    def get_user_by_id(self, user_id):
        user = self.db.find_first_object(User, id=user_id)
        if user is not None:
            return self.get_user_info(user)
        else:
            return "Not found", 404

    def get_user_info(self, user):
        return {
            "id": user.id,
            "name": user.name,
            "nickname": user.nickname,
            "email": user.emails.filter_by(primary_email=EmailStatus.Primary).first().email,
            "avatar_url": user.avatar_url,
            "online": user.online,
            "create_time": str(user.create_time),
            "last_login_time": str(user.last_login_time)
        }

    def get_user_detail_info(self, user, **kwargs):
        detail = self.get_user_info(user)

        experiments = user.experiments.filter_by(status=ExprStatus.Running).all()
        detail["experiments"] = []
        map(lambda e: detail["experiments"].append({
            "id": e.id,
            "hackathon_id": e.hackathon_id
        }), experiments)

        detail["register_state"] = True
        hack = hack_manager.get_hackathon_by_name(kwargs['hackathon_name'])
        if hack is not None and safe_get_config('checkRegister', False) == True:
            detail["register_state"] = self.__validate_user_registered(user, hack)

        return detail


user_manager = UserManager(db_adapter)