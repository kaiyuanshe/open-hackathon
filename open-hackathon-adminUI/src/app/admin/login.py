__author__ = 'root'

import sys
import urllib2
sys.path.append("..")
# -*- coding:utf8 -*-
# encoding = utf-8
from app.functions import get_remote, get_config, convert
from app.log import log
import json
from admin_mgr import admin_manager
from flask import session
from flask_login import logout_user


class LoginBase():
    def login2db(self,openid,**kwargs):
        admin_with_token = admin_manager.db_login(openid, **kwargs)
        # login flask
        admin = admin_with_token["admin"]
        log.info("login successfully:" + repr(admin))
        session["token"] = admin_with_token["token"].token
        #TODO session's contents will be appended , such as cookies if we conmunicate with APIservice
        return admin_manager.get_admin_info(admin)

    def logout(self, admin):
        session.pop("token")
        logout_user()
        return admin_manager.db_logout(admin)



class QQLogin(LoginBase):

    def login(self, args):
        log.info('login from QQ')
        code = args.get('code')
        state = "openhackathon"
        # if state != QQ_OAUTH_STATE:
        # log.warn("STATE match fail. Potentially CSFR.")
        # return "UnAuthorized", 401

        # get access token
        token_resp = get_remote(get_config("login/qq/access_token_url") + code + '&state=' + state)
        log.debug("get token from qq:" + token_resp)
        start = token_resp.index('=')
        end = token_resp.index('&')
        access_token = token_resp[start + 1:end]
        # get user info
        # get openID.
        openid_resp = get_remote(get_config("login/qq/openid_url") + access_token)
        log.debug("get access_token from qq:" + access_token)

        info = json.loads(openid_resp[10:-4])
        openid = info['openid']
        log.debug("get client_id from qq:" + openid)
        client_id = info['client_id']
        log.debug("get openid from qq:" + client_id)

        # get user info
        url = get_config("login/qq/user_info_url") % (access_token, client_id, openid)
        user_info_resp = get_remote(url)
        log.debug("get user info from qq:" + user_info_resp)
        user_info = convert(json.loads(user_info_resp))
        email_info = [
            {'name': user_info["nickname"], 'email': None, 'id': id, 'verified': 1, 'primary': 1,
             'nickname': user_info["nickname"], 'avatar_url': user_info["figureurl"]}]

        return self.login2db(openid,
                            name=user_info["nickname"],
                            nickname=user_info["nickname"],
                            access_token=access_token,
                            email_info=email_info,
                            avatar_url=user_info["figureurl"])



class GithubLogin(LoginBase):
    def login(self, args):
        log.info('login from GitHub')
        code = args.get('code')

        # get access_token
        token_resp = get_remote(get_config('login/github/access_token_url') + code)
        log.debug("get token from github:" + token_resp)
        start = token_resp.index('=')
        end = token_resp.index('&')
        access_token = token_resp[start + 1:end]
        # get user info
        # user_info_resp = get_remote(get_config('login/github/user_info_url') + access_token)
        # conn.request('GET',url,'',{'user-agent':'flask'})
        log.debug("get token info from github")

        # get user info
        user_info_resp = get_remote(get_config('login/github/user_info_url') + access_token)
        # conn.request('GET',url,'',{'user-agent':'flask'}):

        # example:
        # "url":"https://api.github.com/users/juniwang","html_url":"https://github.com/juniwang",
        # "followers_url":"https://api.github.com/users/juniwang/followers",        log.debug("get admin user info from " + provider + " : "  + user_info_resp + '\n' )

        # "following_url":"https://api.github.com/users/juniwang/following{/other_user}",
        # "starred_url":"https://api.github.com/users/juniwang/starred{/owner}{/repo}",
        # "gists_url":"https://api.github.com/users/juniwang/gists{/gist_id}",
        # "events_url":"https://api.github.com/users/juniwang/events{/privacy}",
        # {"login":"juniwang","id":8814383,"avatar_url":"https://avatars.githubusercontent.com/u/8814383?v=3","gravatar_id":"",
        # "subscriptions_url":"https://api.github.com/users/juniwang/subscriptions",
        # "received_events_url":"https://api.github.com/users/juniwang/received_events","type":"User","site_admin":false,
        # "name":"Junbo Wang","company":"","blog":"","location":"Shanghai China",
        # "organizations_url":"https://api.github.com/users/juniwang/orgs","repos_url":"https://api.github.com/users/juniwang/repos",
        #
        # "email":"wangjunbo924@gmail.com","hireable":false,"bio":null,"public_repos":12,"public_gists":0,"followers":0,
        # "following":1,"created_at":"2014-09-18T01:30:30Z","updated_at":"2014-11-25T09:00:37Z","private_gists":0,
        # "plan":{"name":"free","space":307200,"collaborators":0,"private_repos":0}}
        # "total_private_repos":0,"owned_private_repos":0,"disk_usage":14179,"collaborators":0,
        #
        user_info = json.loads(user_info_resp)
        name = user_info["login"]
        nickname = user_info["name"] if "name" in user_info else name
        openid = str(user_info["id"])
        avatar = user_info["avatar_url"]
        # get user primary email
        email_info_resp = get_remote(get_config('login/github/emails_info_url') + access_token)
        log.debug("get email from github:" + email_info_resp + '\n')
        # email_info include all user email provided by github
        # email is user's primary email
        email_info = json.loads(email_info_resp)

        return self.login2db(openid, name=name,
                                    nickname=nickname,
                                    access_token=access_token,
                                    email_info=email_info,
                                    avatar_url=avatar)



class GitcafeLogin(LoginBase):
    def login(self, args):
        log.info('login from Gitcafe')
        code = args.get('code')
        url = get_config('login/gitcafe/access_token_url') + code
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url, "")
        # req = requests.post(url, verify=True)
        resp = opener.open(request)
        # log.debug("get token from gitcafe:" + resp.read())
        token_resp = json.loads(resp.read())
        # token_resp = json.loads(resp.read())
        # token_resp = req.content()

        token = token_resp['access_token']
        value = "Bearer " + token
        header = {"Authorization": value}
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(get_config("login/gitcafe/user_info_url"))
        request.add_header("Authorization", value)
        user_info = opener.open(request).read()
        log.debug(user_info)
        info = json.loads(user_info)

        name = info['username']
        email = info['email']
        id = info['id']
        nickname = info['fullname']
        if nickname is None:
            nickname = name
        if info['avatar_url'].startswith('https'):
            avatar_url = info['avatar_url']
        else:
            avatar_url = "https" + info['avatar_url'][4:]
        email_info = [
            {'name': name, 'email': email, 'id': id, 'verified': 1, 'primary': 1, 'nickname': nickname,
             'avatar_url': avatar_url}]

        return self.login2db(id,
                            name=name,
                            nickname=nickname,
                            access_token=token,
                            email_info=email_info,
                            avatar_url=avatar_url)

login_providers = {
    "github": GithubLogin(),
    "qq": QQLogin(),
    "gitcafe": GitcafeLogin()
}