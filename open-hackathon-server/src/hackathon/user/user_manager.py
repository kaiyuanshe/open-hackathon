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

from flask import request, g

from hackathon.hackathon_response import internal_server_error, not_found
from hackathon.database import UserToken, User, UserEmail, UserProfile, AdminHackathonRel
from hackathon.constants import ReservedUser, HTTP_HEADER
from hackathon import Component, RequiredFeature

__all__ = ["UserManager"]


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

    def get_user_by_id(self, user_id):
        """Query user by unique id

        :type user_id: int
        :param user_id: id of the user to query

        :rtype: User
        :return: instance of User or None if user not found
        """
        return self.db.find_first_object_by(User, id=user_id)

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

        keyword = str(args.get("keyword", ""))
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
            admin_hackathon_rel = self.db.find_first_object_by(AdminHackathonRel, hackathon_id=hackathon.id, user_id=user.id)
            user_info["role_type"] = admin_hackathon_rel.role_type if admin_hackathon_rel else 3 # admin:1 judge:2 user:3
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
            "last_login_time": str(user.last_login_time)
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

    # ----------------------------private methods-------------------------------------

    def __validate_token(self, token):
        """Validate token to make sure it exists and not expired

        :type token: str|unicode
        :param token: token strin

        :rtype: User
        :return user related to the token or None if token is invalid
        """
        t = self.db.find_first_object_by(UserToken, token=token)
        if t is not None and t.expire_date >= self.util.get_now():
            return t.user

        return None
