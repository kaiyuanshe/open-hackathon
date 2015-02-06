__author__ = 'root'

# -*- coding:utf8 -*-
# encoding = utf-8
from functions import get_remote, get_config, post_to_remote
import urllib2
from log import log
import json
from flask import redirect, url_for

hackathon_api_url = get_config("hackathon-api/endpoint")
hackathon_name = get_config("javascript/hackathon/name")


class LoginUser:
    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.name = kwargs["name"]
        self.nickname = kwargs["nickname"]
        self.avatar_url = kwargs["avatar_url"]

    def is_authenticated(self):
        return True

    def is_active(self):
        return True


    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class QQLogin():
    def login(self, args):
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
        data = {"provider": "qq", "access_token": access_token}
        # url = get_config("login/qq/user_info_url") % (access_token, client_id, openid)
        return post_to_remote('%s/api/user/login' % hackathon_api_url, data)


class GithubLogin():
    def login(self, args):
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
        data = {"provider": "github", "code": code, "access_token": access_token, "hackathon_name": hackathon_name}
        return post_to_remote('%s/api/user/login' % hackathon_api_url, data)
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


class GitcafeLogin():
    def login(self, args):
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
        data = {"provider": "gitcafe", "access_token": token_resp['access_token']}
        return post_to_remote('%s/api/user/login' % hackathon_api_url, data)


login_providers = {
    "github": GithubLogin(),
    "qq": QQLogin(),
    "gitcafe": GitcafeLogin()
}