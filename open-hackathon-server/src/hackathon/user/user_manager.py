# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""
import uuid
import json
from datetime import timedelta, datetime

from flask import request, g
from mongoengine import Q, NotUniqueError, ValidationError

from hackathon.hackathon_response import bad_request, internal_server_error, not_found, ok, unauthorized
from hackathon.constants import HTTP_HEADER, HACK_USER_TYPE, FILE_TYPE
from hackathon import Component, Context, RequiredFeature
from hackathon.hmongo.models import UserToken, User, UserEmail, UserProfile, UserHackathon
from hackathon.util import get_remote, get_config

__all__ = ["UserManager"]

users_operation_time = {}


class UserManager(Component):
    """Component for user management"""
    admin_manager = RequiredFeature("admin_manager")
    oauth_login_manager = RequiredFeature("oauth_login_manager")

    def validate_token(self):
        """Make sure user token is included in http request headers and it must NOT be expired

        If valid token is found , the related user will be set int flask global g. So you can access g.user to get the
        current login user throughout the request. There is no need to query user from DB again.

        :rtype: bool
        :return True if valid token found in DB otherwise False
        """
        if HTTP_HEADER.AUTHORIZATION not in request.headers:
            return False

        user = self.__validate_token(request.headers[HTTP_HEADER.AUTHORIZATION])
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
            g.user = None
            g.token.delete()
            return ok()
        except Exception as e:
            self.log.error(e)
            return internal_server_error(e.message)

    def login(self, provider, context):
        if provider == "db":
            return self.__db_login(context)
        else:
            return self.__oauth_login(provider, context)

    def authing(self, context):
        token = context.token
        username = context.username

        if not token or not username:
            self.log.info(
                "Unable to handle authing login request. Either token or username is empty. username: " % username)
            return unauthorized("Unable to handle authing login request. Either token or username is empty")

        # validate access token
        self.log.info("Validate authing token for user %s" % username)
        validate_url = get_config("login.authing.validate_token_url") + token
        validate_raw_resp = get_remote(validate_url)
        validate_resp = json.loads(validate_raw_resp)

        if int(validate_resp["code"]) != 200 or not bool(validate_resp["status"]):
            self.log.info("Token invalid: %s" % validate_raw_resp)
            return unauthorized("Token invalid: %s" % validate_raw_resp)

        authing_id = context._id
        open_id = context.unionid
        provider = context.registerMethod
        if "oauth" in provider:
            # OAuth like github. registerMethod example: "oauth:github"
            provider = provider[6:]
        else:
            # Authing user: using authing_id as open_id
            open_id = authing_id

        email_list = [{
            "email": context.get("email", ""),
            "primary": True,
            "verified": bool(context.get("emailVerified", False))
        }]

        user = self.__get_existing_user(open_id, provider)
        if user is not None:
            nickname = context.get("nickname", user.nickname)
            if not nickname:
                nickname = user.name
            user.update(
                name=context.get("username", user.name),
                nickname=nickname,
                access_token=context.get("token", user.access_token),
                avatar_url=context.get("photo", user.avatar_url),
                authing_id=authing_id,
                last_login_time=self.util.get_now(),
                login_times=user.login_times + 1,
                online=True)
            list(map(lambda x: self.__create_or_update_email(user, x), email_list))
        else:
            user = User(openid=open_id,
                        name=username,
                        provider=provider,
                        authing_id=authing_id,
                        nickname=context.nickname,
                        access_token=token,
                        avatar_url=context.get("photo", ""),
                        login_times=int(context.get("loginsCount", "1")),
                        online=True)

            try:
                user.save()
            except ValidationError as e:
                self.log.error(e)
                return internal_server_error("create user fail.")

            list(map(lambda x: self.__create_or_update_email(user, x), email_list))

        # save API token
        token_expire_date = self.util.get_now() + timedelta(hours=1)
        if "tokenExpiredAt" in context:
            try:
                token_expire_date = datetime.strptime(context.tokenExpiredAt, '%a %b %d %Y %H:%M:%S GMT%z (CST)')
            except Exception as e:
                self.log.warn("Unable to parse tokenExpiredAt: %s. Will use 1 hour as expiry." % context.tokenExpiredAt)
        else:
            self.log.info("tokenExpiredAt not included in authing response. Will use 1 hour as expiry.")

        user_token = UserToken(token=token,
                               user=user,
                               expire_date=token_expire_date)
        user_token.save()
        # resp = {
        #     "token": user_token.dic(),
        #     "user": user.dic()
        # }
        resp = context.to_dict()
        resp.update(user.dic())
        return resp

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
        # fixme why delete this log will panic
        self.log.debug("get talents {}".format(users))
        return [self.user_display_info(u) for u in users]

    @staticmethod
    def update_user_avatar_url(user, url):
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
                # save token to g, to determine which one to remove, when logout
                g.token = t
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
            return unauthorized("username or password error")

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
        self.log.info("Oauth login with %s and code: %s" % (provider, context.code))
        oauth_resp = self.oauth_login_manager.oauth_login(provider, context)
        return self.__oauth_login_db(provider, Context.from_object(oauth_resp))

    def __oauth_login_db(self, provider, context):
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
            list(map(lambda x: self.__create_or_update_email(user, x), email_list))
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

            list(map(lambda x: self.__create_or_update_email(user, x), email_list))

        # generate API token
        token = self.__generate_api_token(user)
        resp = {
            "token": token.dic(),
            "user": user.dic()}
        return resp

    def __generate_file_name(self, user_id, type, suffix):
        # may generate differrnt file_names for different type. see FILE_TYPE.
        file_name = "%s-%s%s" % (str(user_id), str(uuid.uuid1())[0:8], suffix)
        return file_name

    def __validate_upload_files(self):
        # todo check file size and file type
        # if request.content_length > len(request.files) * self.util.get_config("storage.size_limit_kilo_bytes") * 1024:
        #    raise BadRequest("more than the file size limited")

        # check each file type and only jpg is allowed
        # for file_name in request.files:
        #    if request.files.get(file_name).filename.endswith('jpg'):
        #        continue  # jpg is not considered in imghdr
        #    if imghdr.what(request.files.get(file_name)) is None:
        #        raise BadRequest("only images can be uploaded")
        pass
