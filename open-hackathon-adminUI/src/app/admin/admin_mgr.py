# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------

import sys

sys.path.append("..")
from app.database.models import *
from app.log import log
from app.database import db_adapter
from app.constants import HTTP_HEADER
from app.functions import safe_get_config, get_now
from flask import request, g
import uuid
from app.md5 import encode
from datetime import timedelta


class AdminManager(object):
    def __init__(self, db_adapter):
        self.db = db_adapter

    def __generate_api_token(self, admin):
        token_issue_date = get_now()
        token_expire_date = token_issue_date + timedelta(
            minutes=safe_get_config("login/token_expiration_minutes", 1440))
        user_token = UserToken(token=str(uuid.uuid1()),
                               user=admin,
                               expire_date=token_expire_date,
                               issue_date=token_issue_date)
        self.db.add_object(user_token)
        return user_token

    def __validate_token(self, token):
        t = self.db.find_first_object(UserToken, token=token)
        if t is not None and t.expire_date >= get_now():
            return t.user
        return None

    def __create_or_update_email(self, user, email_info):
        email = email_info['email']
        primary_email = email_info['primary']
        verified = email_info['verified']
        existed = self.db.find_first_object_by(UserEmail, email=email)
        if existed is None:
            user_email = UserEmail(name=user.name,
                                   email=email,
                                   primary_email=primary_email,
                                   verified=verified,
                                   user=user)
            self.db.add_object(user_email)
        else:
            existed.primary_email = primary_email
            existed.verified = verified
            existed.name = user.name
            self.db.commit()

    def __get_existing_user(self, openid, email_list):
        # find user by email first in case that email registered in multiple oauth providers
        emails = [e["email"] for e in email_list]
        if len(emails):
            ues = self.db.find_first_object(UserEmail, UserEmail.email.in_(emails))
            if ues is not None:
                return ues.user

        return self.db.find_first_object_by(User, openid=openid)

    def db_logout(self, admin):
        try:
            self.db.update_object(admin, online=0)
            self.db.commit()
            return True
        except Exception as e:
            log.error(e)
            return False

    def mysql_login(self, user, pwd):
        enc_pwd = encode(pwd)
        admin = self.db.find_first_object_by(User, name=user, password=enc_pwd)
        if admin is None:
            log.warn("invalid user/pwd login: user=%s, encoded pwd=%s" % (user, enc_pwd))
            return None

        token = self.__generate_api_token(admin)
        return {
            "token": token,
            "admin": admin
        }

    def oauth_db_login(self, openid, **kwargs):
        # update db
        email_list = kwargs['email_list']
        admin = self.__get_existing_user(openid, email_list)
        if admin is not None:
            self.db.update_object(admin,
                                  provider=kwargs["provider"],
                                  name=kwargs["name"],
                                  nickname=kwargs["nickname"],
                                  access_token=kwargs["access_token"],
                                  avatar_url=kwargs["avatar_url"],
                                  last_login_time=get_now(),
                                  online=1)
            map(lambda x: self.__create_or_update_email(admin, x), email_list)
        else:
            admin = User(openid=openid,
                         name=kwargs["name"],
                         provider=kwargs["provider"],
                         nickname=kwargs["nickname"],
                         access_token=kwargs["access_token"],
                         avatar_url=kwargs["avatar_url"],
                         online=1)

            self.db.add_object(admin)
            map(lambda x: self.__create_or_update_email(admin, x), email_list)

        # generate API token
        token = self.__generate_api_token(admin)
        self.db.commit()
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
        return self.db.find_first_object_by(User, id=id)

    def get_admin_info(self, admin):
        return {
            "id": admin.id,
            "name": admin.name,
            "nickname": admin.nickname,
            "emails": [e.dic() for e in admin.emails.all()],
            "avatar_url": admin.avatar_url,
            "online": admin.online,
            "create_time": str(admin.create_time),
            "last_login_time": str(admin.last_login_time)
        }

    def get_hackid_from_adminid(self, admin_id):

        admin_user_hackathon_rels = self.db.find_all_objects_by(AdminHackathonRel, user_id=admin_id)
        if len(admin_user_hackathon_rels) == 0:
            return []

        # get hackathon_ids_from AdminUserHackathonRels details
        hackathon_ids = map(lambda x: x.hackathon_id, admin_user_hackathon_rels)
        return list(set(hackathon_ids))

    def check_role(self, role):
        hackathon_ids = self.get_hackid_from_adminid(g.admin.id)
        return -1 in hackathon_ids or len(hackathon_ids) > 0

    def is_super(self, admin_id):
        return -1 in self.get_hackid_from_adminid(admin_id)


admin_manager = AdminManager(db_adapter)


def is_super(admin):
    return admin_manager.is_super(admin.id)


User.is_super = is_super
