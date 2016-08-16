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
import uuid

from flask import request, g
from mongoengine import Q, NotUniqueError, ValidationError

from hackathon.hackathon_response import bad_request, internal_server_error, not_found, ok
from hackathon.constants import HTTP_HEADER, HACK_USER_TYPE, FILE_TYPE
from hackathon import Component, Context, RequiredFeature
from hackathon.hmongo.models import UserToken, User, UserEmail, UserProfile, UserHackathon

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
                user.online = False
                user.save()
            return ok()
        except Exception as e:
            self.log.error(e)
            return internal_server_error(e.message)

    def login(self, provider, context):
        if provider == "db":
            return self.__db_login(context)
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
        else:
            time_interval = timedelta(hours=self.util.safe_get_config("login.token_valid_time_minutes", 60))
            new_toke_time = self.util.get_now() + time_interval
            UserToken.objects(token=request.headers[HTTP_HEADER.TOKEN]).update(expire_date=new_toke_time)

        users_operation_time[user.id] = self.util.get_now()

        return True

    def check_user_online_status(self):
        """Check whether the user is offline. If the answer is yes, update its status in DB."""
        overtime_user_ids = [user_id for user_id in users_operation_time
                             if (self.util.get_now() - users_operation_time[user_id]).seconds > 3600]
        # 3600s- expire as token expire

        User.objects(id__in=overtime_user_ids).update(online=False)
        for user_id in overtime_user_ids:
            users_operation_time.pop(user_id, "")

    def get_user_by_id(self, user_id):
        """Query user by unique id

        :type user_id: str
        :param user_id: _id of the user to query

        :rtype: User
        :return: instance of User or None if user not found
        """
        return User.objects(id=user_id).first()

    def load_user(self, user_id):
        '''get user for flask_login user_loader'''
        user = self.get_user_by_id(user_id)
        dic = user.dic() if user else not_found()
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

        return User.objects(emails__email=email).first()

    def get_user_fezzy_search(self, hackathon, args):
        """fezzy search user by name, nickname and email

        :type **kwargs: dict
        :param **kwargs: dict should has key['condition']

        :rtype: list
        :return a list of users or empty list if not user match conditions
        """

        keyword = args.get("keyword", "")
        page = int(args.get("page", 1))
        per_page = int(args.get("per_page", 20))

        pagination = User.objects(
            Q(name__icontains=keyword) |
            Q(nickname__icontains=keyword) |
            Q(emails__email__icontains=keyword)).paginate(page, per_page)

        def get_user_details(user):
            user_info = self.user_display_info(user)

            user_hackathon = UserHackathon.objects(hackathon=hackathon, user=user).first()
            user_info["role"] = user_hackathon.role if user_hackathon else HACK_USER_TYPE.VISITOR
            user_info["remark"] = user_hackathon.remark if user_hackathon else ""

            return user_info

        # return serializable items as well as total count
        return self.util.paginate(pagination, get_user_details)

    def cleaned_user_dic(self, user):
        """trim the harmful and security info from the user object

        this function return the cleaned info that can return to low-security client
        such as web browser

        :type user: User
        :param user: User instance to be cleaned

        :rtype: dict
        :return: cleaned user dict
        """
        ret = user.dic()

        # pop high-security-risk data
        if "password" in ret:
            ret.pop("password")
        if "access_token" in ret:
            ret.pop("access_token")

        return ret

    def user_display_info(self, user):
        """Return user detail information

        Sensitive information like password is filtered
        Other info such as email, profile will be returned too to decrease http request times.

        :type user: User
        :param user: User instance to be returned which shouldn't be None

        :rtype dict
        :return user detail info from collection User
        """
        if user is None:
            return None

        ret = self.cleaned_user_dic(user)

        # set avatar_url to display
        if "profile" in ret and "avatar_url" in ret["profile"]:
            ret["avatar_url"] = ret["profile"]["avatar_url"]

        return ret

    def get_talents(self):
        # todo real talents list
        users = User.objects(name__ne="admin").order_by("-login_times")[:10]

        return [self.user_display_info(u) for u in users]

    def update_user_avatar_url(self, user, url):
        if not user.profile:
            user.profile = UserProfile()
        user.profile.avatar_url = url
        user.save()
        return True

    def upload_files(self, user_id, file_type):
        """Handle uploaded files from http request"""
        try:
            self.__validate_upload_files()
        except Exception as e:
            self.log.error(e)
            return bad_request("file size or file type unsupport")

        file_list = []
        storage = RequiredFeature("storage")
        for file in request.files:
            file_content = request.files[file]
            pre_file_name = file_content.filename
            file_suffix = pre_file_name[pre_file_name.rfind('.'):]
            new_file_name = self.__generate_file_name(user_id, file_type, file_suffix)
            self.log.debug("upload file: " + new_file_name)
            context = Context(
                file_name=new_file_name,
                file_type=file_type,
                content=file_content
            )
            context = storage.save(context)

            # file_name is a random name created by server, pre_file_name is the original name
            file_info = {
                "file_name": new_file_name,
                "pre_file_name": pre_file_name,
                "url": context.url
            }
            file_list.append(file_info)
        return {"files": file_list}

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
            # todo eliminate the warning related to 'objects'
            t = UserToken.objects(token=token).first()
            if t and t.expire_date >= self.util.get_now():
                g.authenticated = True
                g.user = t.user
                return t.user

        return None

    def __generate_api_token(self, admin):
        token_issue_date = self.util.get_now()
        valid_period = timedelta(minutes=self.util.safe_get_config("login.token_valid_time_minutes", 60))
        token_expire_date = token_issue_date + valid_period
        user_token = UserToken(token=str(uuid.uuid1()),
                               user=admin,
                               expire_date=token_expire_date,
                               issue_date=token_issue_date)
        user_token.save()
        return user_token

    def __db_login(self, context):
        username = context.get("username")
        enc_pwd = context.get("password")

        user = User.objects(name=username, password=enc_pwd).first()
        if user is None:
            self.log.warn("invalid user/pwd login: username=%s, encoded pwd=%s" % (username, enc_pwd))
            return None

        user.online = True
        user.login_times = (user.login_times or 0) + 1
        user.save()

        token = self.__generate_api_token(user)
        return {
            "token": token.dic(),
            "user": user.dic()}

    def __create_or_update_email(self, user, email_info):
        email = email_info['email']
        primary_email = email_info['primary']
        verified = email_info['verified']

        new_mail = UserEmail(
            email=email,
            primary_email=primary_email,
            verified=verified)

        existed = False
        for i, e in enumerate(user.emails):
            if e.email == email:
                user.emails[i] = new_mail
                existed = True
                break

        if not existed:
            user.emails.append(new_mail)

        user.save()

    def __get_existing_user(self, openid, provider):
        return User.objects(openid=openid, provider=provider).first()

    def __oauth_login(self, provider, context):
        # update db
        email_list = context.get('email_list', [])
        openid = context.openid

        user = self.__get_existing_user(openid, provider)
        if user is not None:
            user.update(
                provider=provider,
                name=context.get("name", user.name),
                nickname=context.get("nickname", user.nickname),
                access_token=context.get("access_token", user.access_token),
                avatar_url=context.get("avatar_url", user.avatar_url),
                last_login_time=self.util.get_now(),
                login_times=user.login_times + 1,
                online=True)
            map(lambda x: self.__create_or_update_email(user, x), email_list)
        else:
            user = User(openid=openid,
                        name=context.name,
                        provider=provider,
                        nickname=context.nickname,
                        access_token=context.access_token,
                        avatar_url=context.get("avatar_url", ""),
                        login_times=1,
                        online=True)

            try:
                user.save()
            except ValidationError as e:
                self.log.error(e)
                return internal_server_error("create user fail.")

            map(lambda x: self.__create_or_update_email(user, x), email_list)

        # oxford only
        if provider == "alauda":
            self.__oxford(user, context.get("oxford_api"))

        # generate API token
        token = self.__generate_api_token(user)
        return {
            "token": token.dic(),
            "user": user.dic()}

    def __oxford(self, user, oxford_api):
        if not oxford_api:
            return

            # TODO: not finish
            # hackathon = Hackathon.objects(name="oxford").first()
            # if hackathon:
            #     exist = self.db.find_first_object_by(UserHackathonAsset, asset_value=oxford_api)
            #     if exist:
            #         return
            #
            #     asset = UserHackathonAsset(user_id=user.id,
            #                                hackathon_id=hackathon.id,
            #                                asset_name="Oxford Token",
            #                                asset_value=oxford_api,
            #                                description="Token for Oxford API")
            #     self.db.add_object(asset)
            #     self.db.commit()

    def __generate_file_name(self, user_id, type, suffix):
        # may generate differrnt file_names for different type. see FILE_TYPE.
        file_name = "%s-%s%s" % (str(user_id), str(uuid.uuid1())[0:8], suffix)
        return file_name

    def __validate_upload_files(self):
        # todo check file size and file type
        #if request.content_length > len(request.files) * self.util.get_config("storage.size_limit_kilo_bytes") * 1024:
        #    raise BadRequest("more than the file size limited")

        # check each file type and only jpg is allowed
        #for file_name in request.files:
        #    if request.files.get(file_name).filename.endswith('jpg'):
        #        continue  # jpg is not considered in imghdr
        #    if imghdr.what(request.files.get(file_name)) is None:
        #        raise BadRequest("only images can be uploaded")
        pass
