# -*- coding:utf8 -*-
#encoding = utf-8
from database import *
from functions import *
from log import log
import json
from flask_login import login_user
from flask import request, redirect, session
from constants import *


class LoginBase(object):
    def check_first_user(self, user):
        # make the first login user be the first super admin
        admin = Role.query.filter_by(name="admin").first()
        if admin.users.count() == 0:
            first_admin = UserRole(admin, user)
            db.session.add(first_admin)
            db.session.commit()


class QQLogin(LoginBase):
    def qq_authorized(self):
        code = request.args.get('code')
        state = request.args.get('state')
        if state != QQ_OAUTH_STATE:
            log.warn("STATE match fail. Potentially CSFR.")
            return "UnAuthorized", 401

        # get access token
        token_resp = get_remote(get_config("login/qq/access_token_url") + code + '&state=' + state)
        log.debug("get token from qq:" + token_resp)
        start = token_resp.index('=')
        end = token_resp.index('&')
        access_token = token_resp[start+1:end]

        # get openID.
        openid_resp = get_remote(get_config("login/qq/openid_url") + access_token)
        log.debug("get openid from qq:" + openid_resp)
        info = json.loads(openid_resp[10:-4])
        openid = info['openid']
        client_id = info['client_id']

        # get user info
        url = get_config("login/qq/user_info_url") % (access_token, client_id, openid)
        user_info_resp = get_remote(url)
        log.debug("get user info from qq:" + user_info_resp)
        user_info = convert(json.loads(user_info_resp))

        user = User.query.filter_by(openid=openid).first()
        if user is not None:
            user.access_token = access_token
            user.name = user_info["nickname"]
            user.nickname = user_info["nickname"]
            user.avatar_url = user_info["figureurl"]
            user.last_login_time = datetime.utcnow()
            db.session.commit()
        else:

            user = User(user_info["nickname"],
                    user_info["nickname"],
                    None,
                    openid,
                    user_info["figureurl"],
                    access_token)
            db.session.add(user)
            db.session.commit()

        login_user(user)
        log.info("qq user login successfully:" + repr(user))

        self.check_first_user(user)

        hava_running_expr = Experiment.query.filter_by(user_id=user.id, status=1).count() > 0
        next_url = session["next"] if 'next' in session else None
        if next_url is None:
            next_url = "/hackathon" if hava_running_expr else "/settings"
        else:
            session["next"] = None

        return redirect(next_url)

class GithubLogin(LoginBase):
    def github_authorized(self):
        code = request.args.get('code')

        # get access_token
        token_resp = get_remote(get_config('login/github/access_token_url') + code)
        log.debug("get token from github:" + token_resp)
        start = token_resp.index('=')
        end = token_resp.index('&')
        access_token = token_resp[start+1:end]

        # get user info
        user_info_resp = get_remote(get_config('login/github/user_info_url') + access_token)
        # conn.request('GET',url,'',{'user-agent':'flask'})
        log.debug("get user info from github:" + user_info_resp)
        # example:
        #
        # {"login":"juniwang","id":8814383,"avatar_url":"https://avatars.githubusercontent.com/u/8814383?v=3","gravatar_id":"",
        # "url":"https://api.github.com/users/juniwang","html_url":"https://github.com/juniwang",
        # "followers_url":"https://api.github.com/users/juniwang/followers",
        # "following_url":"https://api.github.com/users/juniwang/following{/other_user}",
        # "gists_url":"https://api.github.com/users/juniwang/gists{/gist_id}",
        # "starred_url":"https://api.github.com/users/juniwang/starred{/owner}{/repo}",
        # "subscriptions_url":"https://api.github.com/users/juniwang/subscriptions",
        # "organizations_url":"https://api.github.com/users/juniwang/orgs","repos_url":"https://api.github.com/users/juniwang/repos",
        # "events_url":"https://api.github.com/users/juniwang/events{/privacy}",
        # "received_events_url":"https://api.github.com/users/juniwang/received_events","type":"User","site_admin":false,
        # "name":"Junbo Wang","company":"","blog":"","location":"Shanghai China",
        # "email":"wangjunbo924@gmail.com","hireable":false,"bio":null,"public_repos":12,"public_gists":0,"followers":0,
        # "following":1,"created_at":"2014-09-18T01:30:30Z","updated_at":"2014-11-25T09:00:37Z","private_gists":0,
        # "total_private_repos":0,"owned_private_repos":0,"disk_usage":14179,"collaborators":0,
        # "plan":{"name":"free","space":307200,"collaborators":0,"private_repos":0}}
        #
        user_info = json.loads(user_info_resp)
        name = user_info["login"]
        nickname = user_info["name"] if "name" in user_info else name
        openid = str(user_info["id"])
        avatar = user_info["avatar_url"]

        # get user primary email
        email_info_resp = get_remote(get_config('login/github/emails_info_url') + access_token)
        log.debug("get email from github:" + email_info_resp)
        email_info = json.loads(email_info_resp)
        email = filter(lambda e: e["primary"], email_info)[0]["email"]
        # email = ",".join(map(lambda e: e["email"], email_info))

        log.info("successfully get email:" + email)
        user = User.query.filter_by(openid=openid).first()
        if user is not None:
            user.name = name
            user.nickname = nickname
            user.access_token = access_token
            user.email = email
            user.avatar_url = avatar
            user.last_login_time = datetime.utcnow()
            db.session.commit()
        else:
            user = User(name, nickname, email, openid, avatar, access_token)
            db.session.add(user)
            db.session.commit()

        # login user so that flask-login can manage session and cookies
        login_user(user)
        log.info("github user login successfully:" + repr(user))

        self.check_first_user(user)

        # find out the hackacathon registration info
        is_registration_limited = safe_get_config("/register/limitUnRegisteredUser", True)
        registered = Registration().get_by_email(email)

        is_admin = user.is_admin()
        is_not_registered = is_registration_limited and registered is None
        hava_running_expr = Experiment.query.filter_by(user_id=user.id, status=1).count() > 0

        next_url = session["next"] if 'next' in session else None
        if next_url is None:
            next_url = "/hackathon" if hava_running_expr else "/settings"
        else:
            session["next"] = None

        if is_not_registered:
            if is_admin:
                return redirect(next_url)
            else:
                log.info("github user login successfully but not registered. Redirect to registration page")
                return redirect("/notregister")
        else:
            registered.online = 1
            db.session.commit()
            return redirect(next_url)

