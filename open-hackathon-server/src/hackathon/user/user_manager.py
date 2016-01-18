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

from datetime import timedelta

from sqlalchemy.exc import IntegrityError
from flask import request, g
import uuid

from hackathon.hackathon_response import internal_server_error, not_found, ok
from hackathon.database import UserToken, User, UserEmail, AdminHackathonRel, Hackathon, UserHackathonAsset
from hackathon.constants import ReservedUser, HTTP_HEADER
from hackathon import Component, RequiredFeature

__all__ = ["UserManager"]

users_operation_time = {}

class UserManager(Component):
    """Component for user management"""
    admin_manager = RequiredFeature("admin_manager")

    def validate_login(self):
        """Make sure user token is included in http request headers and it must NOT be expired

        If valid token is found , the related user will be set int flask global g. So you can access g.user to get the
        current login user throughout the request. There is no need to query user from DB again.

        :rtype: bool
        :return True if valid token found in DB otherwise False
        """
        if HTTP_HEADER.TOKEN not in request.headers:
            return False

        user = self.__validate_token(request.headers[HTTP_HEADER.TOKEN])
        if user is None:
            return False

        g.user = user
        return True

    def logout(self, user_id):
        try:
            user = self.get_user_by_id(user_id)
            if user:
                user.online = 0
                self.db.commit()
            return ok()
        except Exception as e:
            self.log.error(e)
            return internal_server_error(e.message)

    def login(self, provider, context):
        if provider == "mysql":
            return self.__mysql_login(context)
        else:
            return self.__oauth_login(provider, context)

    def update_user_operation_time(self):
        """Update the user's last operation time.

        :rtype:bool
        :return True if success in updating, return False if token not found or token is overtime.
        """
        if HTTP_HEADER.TOKEN not in request.headers:
            return False

        user = self.__validate_token(request.headers[HTTP_HEADER.TOKEN])
        if user is None:
            return False

        users_operation_time[user.id] = self.util.get_now()
        return True

    def check_user_online_status(self):
        """Check whether the user is offline. If the answer is yes, update its status in DB."""
        overtime_user_ids = [user_id for user_id in users_operation_time
                             if (self.util.get_now() - users_operation_time[user_id]).seconds > 1800] # 1800s-half hour

        User.query.filter(User.id.in_(overtime_user_ids)).update({User.online: 0}, synchronize_session=False)
        self.db.commit()
        for user_id in overtime_user_ids:
            users_operation_time.pop(user_id, "")

    def get_user_by_id(self, user_id):
        """Query user by unique id

        :type user_id: int
        :param user_id: id of the user to query

        :rtype: User
        :return: instance of User or None if user not found
        """
        return self.db.find_first_object_by(User, id=user_id)

    def load_user(self, user_id):
        '''get user for flask_login user_loader'''
        user = self.get_user_by_id(user_id)
        dic = user.dic() if user else not_found()
        dic["is_super"] = self.is_super_admin(user)
        return dic

    def get_user_by_email(self, email):
        """Query user by email

        :type email: str|unicode
        :param email: email address

        :rtype: User
        :return instance of User or None if user cannot be found
        """
        if email is None:
            return None

        user_email = self.db.find_first_object_by(UserEmail, email=email)
        if user_email is None:
            return None

        return user_email.user

    def get_user_fezzy_search(self, hackathon, args):
        """fezzy search user by name,kickname and email

        :type **kwargs: dict
        :param **kwargs: dict should has key['condition']

        :rtype: list
        :return a list of users or empty list if not user match conditions
        """

        keyword = args.get("keyword", "")
        page = int(args.get("page", 1))
        per_page = int(args.get("per_page", 20))

        query = User.query
        query = query.outerjoin(UserEmail).filter(User.name.like("%" + keyword + "%") |
                                                  User.nickname.like("%" + keyword + "%") |
                                                  UserEmail.email.like("%" + keyword + "%"))

        # perform db query with pagination
        pagination = self.db.paginate(query, page, per_page)

        def get_user_details(user):
            user_info = self.user_display_info(user)
            admin_hackathon_rel = self.db.find_first_object_by(AdminHackathonRel, hackathon_id=hackathon.id,
                                                               user_id=user.id)
            user_info[
                "role_type"] = admin_hackathon_rel.role_type if admin_hackathon_rel else 3  # admin:1 judge:2 user:3
            user_info["remarks"] = admin_hackathon_rel.remarks if admin_hackathon_rel else ""

            return user_info

        # return serializable items as well as total count
        return self.util.paginate(pagination, get_user_details)

    def user_display_info(self, user):
        """Return user detail information

        Sensitive information like password is filtered
        Other info such as email, profile will be returned too to decrease http request times.

        :type user: User
        :param user: User instance to be returned which shouldn't be None

        :rtype dict
        :return user detail info from table User, UserEmail, UserProfile
        """
        if user is None:
            return None

        ret = {
            "id": user.id,
            "name": user.name,
            "nickname": user.nickname,
            "email": [e.dic() for e in user.emails.all()],
            "provider": user.provider,
            "avatar_url": user.avatar_url,
            "online": user.online,
            "create_time": str(user.create_time),
            "last_login_time": str(user.last_login_time),
            "is_super": self.is_super_admin(user)
        }
        if user.profile:
            ret["user_profile"] = user.profile.dic()

        return ret

    def is_super_admin(self, user):
        """Check whether an user is super admin or not

        super admin is also known as system administrator who have the highest privileges

        :type user: User
        :param user: User instance to be returned which shouldn't be None

        :rtype bool
        :return True if user is super admin otherwise False
        """
        if user.id == ReservedUser.DefaultSuperAdmin:
            return True

        return -1 in self.admin_manager.get_entitled_hackathon_ids(user.id)

    def get_talents(self):
        # todo real talents list
        users = self.db.find_all_objects_order_by(User,
                                                  10,
                                                  User.login_times.desc())
        return [self.user_display_info(u) for u in users]


    def update_user_avatar_url(self, user, url):
        self.db.update_object(user, avatar_url=url)
        return True
    # ----------------------------private methods-------------------------------------

    def __validate_token(self, token):
        """Validate token to make sure it exists and not expired

        :type token: str|unicode
        :param token: token strin

        :rtype: User
        :return user related to the token or None if token is invalid
        """
        if "authenticated" in g and g.authenticated:
            return g.user
        else:
            t = self.db.find_first_object_by(UserToken, token=token)
            if t is not None and t.expire_date >= self.util.get_now():
                g.authenticated = True
                g.user = t.user
                return t.user

        return None

    def __generate_api_token(self, admin):
        token_issue_date = self.util.get_now()
        valid_period = timedelta(minutes=self.util.safe_get_config("login/token_expiration_minutes", 1440))
        token_expire_date = token_issue_date + valid_period
        user_token = UserToken(token=str(uuid.uuid1()),
                               user=admin,
                               expire_date=token_expire_date,
                               issue_date=token_issue_date)
        self.db.add_object(user_token)
        return user_token

    def __mysql_login(self, context):
        username = context.get("username")
        enc_pwd = context.get("password")

        user = self.db.find_first_object_by(User, name=username, password=enc_pwd)
        if user is None:
            self.log.warn("invalid user/pwd login: user=%s, encoded pwd=%s" % (user, enc_pwd))
            return None

        user.online = 1
        self.db.commit()

        token = self.__generate_api_token(user)
        return {
            "token": token.dic(),
            "user": user.dic()
        }

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

    def __get_existing_user(self, openid, provider):
        # emails = [e["email"] for e in email_list]
        # if len(emails):
        #     ues = self.db.find_first_object(UserEmail, UserEmail.email.in_(emails))
        #     if ues is not None:
        #         return ues.user
        return self.db.find_first_object_by(User, openid=openid, provider=provider)

    def __oauth_login(self, provider, context):
        # update db
        email_list = context.get('email_list', [])
        openid = context.openid

        user = self.__get_existing_user(openid, provider)
        if user is not None:
            self.db.update_object(user,
                                  provider=provider,
                                  name=context.get("name", user.name),
                                  nickname=context.get("nickname", user.nickname),
                                  access_token=context.get("access_token", user.access_token),
                                  avatar_url=context.get("avatar_url", user.avatar_url),
                                  last_login_time=self.util.get_now(),
                                  login_times=user.login_times + 1,
                                  online=1)
            map(lambda x: self.__create_or_update_email(user, x), email_list)
        else:
            user = User(openid=openid,
                        name=context.name,
                        provider=provider,
                        nickname=context.nickname,
                        access_token=context.access_token,
                        avatar_url=context.get("avatar_url", ""),
                        login_times=1,
                        online=1)

            try:
                self.db.add_object(user)
            except IntegrityError as e:
                if "1062" in e.message:
                    return self.__oauth_login(provider, context)
                else:
                    raise

            map(lambda x: self.__create_or_update_email(user, x), email_list)

        # oxford only
        if provider == "alauda":
            self.__oxford(user, context.get("oxford_api"))

        # generate API token
        token = self.__generate_api_token(user)
        return {
            "token": token.dic(),
            "user": user.dic()
        }

    def __oxford(self, user, oxford_api):
        if not oxford_api:
            return

        hackathon = self.db.find_first_object_by(Hackathon, name="oxford")
        if hackathon:
            exist = self.db.find_first_object_by(UserHackathonAsset, asset_value=oxford_api)
            if exist:
                return

            asset = UserHackathonAsset(user_id=user.id,
                                       hackathon_id=hackathon.id,
                                       asset_name="Oxford Token",
                                       asset_value=oxford_api,
                                       description="Token for Oxford API")
            self.db.add_object(asset)
            self.db.commit()

