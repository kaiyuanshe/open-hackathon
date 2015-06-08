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
from hackathon.database.models import UserToken, User, UserEmail
from datetime import timedelta
from hackathon.constants import HTTP_HEADER
from hackathon.hackathon_response import not_found
from flask import request, g
import uuid
from hackathon import Component


class UserManager(Component):
    def __generate_api_token(self, user):
        token_issue_date = self.util.get_now()
        token_expire_date = token_issue_date + timedelta(
            minutes=self.util.safe_get_config("login.token_expiration_minutes", 1440))
        user_token = UserToken(token=str(uuid.uuid1()), user=user, expire_date=token_expire_date,
                               issue_date=token_issue_date)
        self.db.add_object(user_token)
        return user_token

    def __validate_token(self, token):
        t = self.db.find_first_object_by(UserToken, token=token)
        if t is not None and t.expire_date >= self.util.get_now():
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


    def db_logout(self, user):
        try:
            self.db.update_object(user, online=0)
            return "OK"
        except Exception as e:
            self.log.error(e)
            return "log out failed"

    def db_login(self, openid, **kwargs):
        # update db
        email_list = kwargs['email_list']
        user = self.__get_existing_user(openid, email_list)
        if user is not None:
            self.db.update_object(user,
                                  name=kwargs["name"],
                                  nickname=kwargs["nickname"],
                                  provider=kwargs["provider"],
                                  access_token=kwargs["access_token"],
                                  avatar_url=kwargs["avatar_url"],
                                  last_login_time=self.util.get_now(),
                                  online=1)
            map(lambda x: self.__create_or_update_email(user, x), email_list)
        else:
            user = User(openid=openid,
                        provider=kwargs["provider"],
                        name=kwargs["name"],
                        nickname=kwargs["nickname"],
                        access_token=kwargs["access_token"],
                        avatar_url=kwargs["avatar_url"],
                        online=1)

            self.db.add_object(user)
            map(lambda x: self.__create_or_update_email(user, x), email_list)

        # generate API token
        token = self.__generate_api_token(user)
        return {
            "token": token,
            "user": user
        }

    def validate_login(self):
        if HTTP_HEADER.TOKEN not in request.headers:
            return False

        user = self.__validate_token(request.headers[HTTP_HEADER.TOKEN])
        if user is None:
            return False

        g.user = user
        return True

    def get_user_by_id(self, user_id):
        user = self.db.find_first_object_by(User, id=user_id)
        if user is not None:
            return self.user_display_info(user)
        else:
            return not_found("user id invalid")

    def user_display_info(self, user):
        return {
            "id": user.id,
            "name": user.name,
            "nickname": user.nickname,
            "email": [e.dic() for e in user.emails.all()],
            "provider": user.provider,
            "avatar_url": user.avatar_url,
            "online": user.online,
            "create_time": str(user.create_time),
            "last_login_time": str(user.last_login_time)
        }


    def get_team_members_by_team_name(self, h_id, t_name):
        team_member = self.db.find_all_objects_by(UserHackathonRel, hackathon_id=h_id, team_name=t_name)

        def get_info(sql_object):
            r = sql_object.dic()
            r['user'] = self.user_display_info(sql_object.user)
            return r

        team_member = map(lambda x: get_info(x), team_member)

        return team_member

    def get_team_members_by_user(self, h_id, u_id):
        my_team = self.db.find_first_object_by(UserHackathonRel, hackathon_id=h_id, user_id=u_id)
        return self.get_team_members_by_team_name(h_id, my_team.team_name)
