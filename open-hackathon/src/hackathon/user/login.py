# -*- coding:utf8 -*-
# encoding = utf-8
from hackathon.functions import get_remote, get_config, convert
from hackathon.log import log
import json
from hackathon.config import QQ_OAUTH_STATE
from . import user_manager
from hackathon.constants import OAUTH_PROVIDER


class LoginProviderBase():
    def login(self, args):
        pass

    def logout(self, user):
        user_manager.db_logout(user)


class QQLogin(LoginProviderBase):
    def login(self, args):
        # code = args.get('code')
        # state = args.get('state')
        # if state != QQ_OAUTH_STATE:
        #    log.warn("STATE match fail. Potentially CSFR.")
        #    return "UnAuthorized", 401

        # get access token
        # token_resp = get_remote(get_config("login/qq/access_token_url") + code + '&state=' + state)
        # log.debug("get token from qq:" + token_resp)
        # start = token_resp.index('=')
        # end = token_resp.index('&')
        access_token = args['access_token']
        openid = args['openid']
        client_id = args['client_id']
        # get openID.
        # openid_resp = get_remote(get_config("login/qq/openid_url") + access_token)
        log.debug("get access_token from qq:" + access_token)
        log.debug("get client_id from qq:" + client_id)
        log.debug("get openid from qq:" + openid)
        # info = json.loads(openid_resp[10:-4])
        # openid = info['openid']
        # client_id = info['client_id']

        # get user info
        url = get_config("login/qq/user_info_url") % (access_token, client_id, openid)
        user_info_resp = get_remote(url)
        log.debug("get user info from qq:" + user_info_resp)
        user_info = convert(json.loads(user_info_resp))

        user_with_token = user_manager.db_login(openid,
                                                name=user_info["nickname"],
                                                nickname=user_info["nickname"],
                                                access_token=access_token,
                                                email=None,
                                                avatar_url=user_info["figureurl"])

        # login flask
        user = user_with_token["user"]
        log.info("QQ user login successfully:" + repr(user))

        detail = user_manager.get_user_detail_info(user)
        detail["token"] = user_with_token["token"].token
        return detail


class GithubLogin(LoginProviderBase):
    def login(self, args):
        access_token = args.get('access_token')
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

        log.info("successfully get email:" + email)
        user_with_token = user_manager.db_login(openid,
                                                name=name,
                                                nickname=nickname,
                                                access_token=access_token,
                                                email=email,
                                                avatar_url=avatar)

        # login flask
        user = user_with_token["user"]
        log.info("github user login successfully:" + repr(user))

        detail = user_manager.get_user_detail_info(user)
        detail["token"] = user_with_token["token"].token
        return detail


login_providers = {
    OAUTH_PROVIDER.GITHUB: GithubLogin(),
    OAUTH_PROVIDER.QQ: QQLogin()
}
