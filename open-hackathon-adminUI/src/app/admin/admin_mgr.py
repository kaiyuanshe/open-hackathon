import sys

sys.path.append("..")
from app.database.models import *
from app.log import log
from app.database import db_adapter
from datetime import datetime, timedelta
from app.constants import HTTP_HEADER, ROLE
from app.enum import EmailStatus
from app.functions import safe_get_config
from flask import request, g
import uuid


class AdminManager(object):
    def __init__(self, db_adapter):
        self.db = db_adapter

    def __generate_api_token(self, admin):
        token_issue_date = datetime.utcnow()
        token_expire_date = token_issue_date + timedelta(
            minutes=safe_get_config("login/token_expiration_minutes", 1440))
        admin_token = AdminToken(token=str(uuid.uuid1()), admin=admin, expire_date=token_expire_date,
                                 issue_date=token_issue_date)
        self.db.add_object(admin_token)
        self.db.commit()
        return admin_token

    def __validate_token(self, token):
        t = self.db.find_first_object(AdminToken, token=token)
        if t is not None and t.expire_date >= datetime.utcnow():
            return t.admin
        return None

    def db_logout(self, admin):
        try:
            self.db.update_object(admin, online=0)
            self.db.commit()
            return "OK"
        except Exception as e:
            log.error(e)
            return "log out failed"

    def db_login(self, openid, **kwargs):
        # update db
        email_info = kwargs['email_info']
        admin = self.db.find_first_object(AdminUser, openid=openid)
        if admin is not None:
            self.db.update_object(admin,
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
                if self.db.find_first_object(AdminEmail, email=email) is None:
                    adminemail = AdminEmail(name=kwargs['name'], email=email, primary_email=primary_email,
                                            verified=verified, admin=admin)
                    self.db.add_object(adminemail)
            self.db.commit()
        else:
            admin = AdminUser(openid=openid,
                              name=kwargs["name"],
                              nickname=kwargs["nickname"],
                              access_token=kwargs["access_token"],
                              avatar_url=kwargs["avatar_url"],
                              online=1)

            self.db.add_object(admin)
            self.db.commit()

            for n in email_info:
                email = n['email']
                primary_email = n['primary']
                verified = n['verified']
                adminemail = AdminEmail(name=kwargs['name'], email=email, primary_email=primary_email,
                                        verified=verified, admin=admin)
                self.db.add_object(adminemail)
                self.db.commit()

        # generate API token
        token = self.__generate_api_token(admin)
        return {
            "token": token,
            "admin": admin
        }

    def validate_request(self):
        if HTTP_HEADER.TOKEN not in request.headers:
            return False

        admin = self.__validate_token(request.headers[HTTP_HEADER.TOKEN])
        if admin is None:
            return False

        g.admin = admin
        return True

    def get_admin_by_id(self, id):
        admin = self.db.find_first_object(AdminUser, id=id)
        if admin is not None:
            return self.get_admin_info(admin)
        else:
            return "Not found", 404

    def get_admin_info(self, admin):
        return {
            "id": admin.id,
            "name": admin.name,
            "nickname": admin.nickname,
            "email": admin.emails.__filter_by(primary_email=EmailStatus.Primary).first().email,
            "avatar_url": admin.avatar_url,
            "online": admin.online,
            "create_time": str(admin.create_time),
            "last_login_time": str(admin.last_login_time)
        }

    def get_hackid_from_adminid(self, admin_id):

        # get emails from admin though admin.id in table admin_email
        admin_emails = self.db.find_all_objects_by(AdminEmail, admin_id=admin_id)
        emails = map(lambda x: x.email, admin_emails)

        # get AdminUserHackathonRels from query withn filter by email
        admin_user_hackathon_rels = self.db.find_all_objects(AdminUserHackathonRel,
                                                             AdminUserHackathonRel.admin_email.in_(emails))
        if len(admin_user_hackathon_rels) == 0:
            return None

        # get hackathon_ids_from AdminUserHackathonRels details
        hackathon_ids = map(lambda x: x.hackathon_id, admin_user_hackathon_rels)
        return list(set(hackathon_ids))

    def check_role(self, role):

        # 0:super admin
        # 1:comman admin

        hackathon_ids = self.get_hackid_from_adminid(g.admin.id)
        # None  or not None { has -1 or has not }

        if hackathon_ids is None:
            return False
        else:
            # only super admin can access
            if role == ROLE.SUPER_ADMIN:
                return -1 in hackathon_ids
            #comman admin all can access
            else:
                return True


admin_manager = AdminManager(db_adapter)