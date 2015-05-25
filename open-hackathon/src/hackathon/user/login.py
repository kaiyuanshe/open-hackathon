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

# -*- coding:utf8 -*-
# encoding = utf-8
import sys

sys.path.append("..")
from hackathon.functions import get_remote, get_config, convert
from hackathon.log import log
from . import user_manager
import json
from hackathon.constants import OAUTH_PROVIDER
from hackathon.hack import hack_manager
from hackathon.registration.register_mgr import register_manager
from hackathon.hackathon_response import *
from hackathon.enum import EStatus


class LoginProviderBase():
    def login(self, args):
        pass

    def logout(self, user):
        return user_manager.db_logout(user)

    def user_display_info_with_token(self, user_with_token):
        user = user_with_token["user"]

        login_result = {
            "user": user_manager.user_display_info(user),
            "token": user_with_token["token"].token
        }
        log.debug("user login successfully:" + repr(login_result))
        return login_result


class QQLogin(LoginProviderBase):
    def __init__(self, user_manager):
        self.um = user_manager

    def login(self, args):
        access_token = args['access_token']
        # get openID.
        openid_resp = get_remote(get_config("login.qq.openid_url") + access_token)
        log.debug("get access_token from qq:" + access_token)

        info = json.loads(openid_resp[10:-4])
        openid = info['openid']
        log.debug("get client_id from qq:" + openid)
        client_id = info['client_id']
        log.debug("get openid from qq:" + client_id)

        # get user info
        url = get_config("login.qq.user_info_url") % (access_token, client_id, openid)
        user_info_resp = get_remote(url)
        log.debug("get user info from qq:" + user_info_resp)
        user_info = convert(json.loads(user_info_resp))
        email_info = [
            {'name': user_info["nickname"], 'email': None, 'id': id, 'verified': 1, 'primary': 1,
             'nickname': user_info["nickname"], 'avatar_url': user_info["figureurl"]}]
        user_with_token = self.um.db_login(openid,
                                           provider=OAUTH_PROVIDER.QQ,
                                           name=user_info["nickname"],
                                           nickname=user_info["nickname"],
                                           access_token=access_token,
                                           email_info=email_info,
                                           avatar_url=user_info["figureurl"])

        # # login flask
        # user = user_with_token["user"]
        # log.info("QQ user login successfully:" + repr(user))
        # hackathon_name = args.get('hackathon_name')
        # detail = self.um.get_user_detail_info(user, hackathon_name=hackathon_name)
        # detail["token"] = user_with_token["token"].token
        # return detail
        return self.user_display_info_with_token(user_with_token)


class GithubLogin(LoginProviderBase):
    def __init__(self, user_manager):
        self.um = user_manager

    def login(self, args):
        access_token = args.get('access_token')
        # get user info

        user_info_resp = get_remote(get_config('login.github.user_info_url') + access_token)
        # conn.request('GET',url,'',{'user-agent':'flask'})
        log.debug("get user info from github:" + user_info_resp + '\n')
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
        email_info_resp = get_remote(get_config('login.github.emails_info_url') + access_token)
        log.debug("get email from github:" + email_info_resp + '\n')
        # email_info include all user email provided by github
        # email is user's primary email
        email_info = json.loads(email_info_resp)
        user_with_token = self.um.db_login(openid,
                                           provider=OAUTH_PROVIDER.GITHUB,
                                           name=name,
                                           nickname=nickname,
                                           access_token=access_token,
                                           email_info=email_info,
                                           avatar_url=avatar)
        return self.user_display_info_with_token(user_with_token)


class GitcafeLogin(LoginProviderBase):
    def __init__(self, user_manager):
        self.um = user_manager

    def login(self, args):
        token = args.get('access_token')
        value = "Bearer " + token
        # opener = urllib2.build_opener(urllib2.HTTPHandler)
        # request = urllib2.Request(get_config("login.gitcafe.user_info_url"))
        # request.add_header("Authorization", value)
        # user_info = opener.open(request).read()

        header = {"Authorization": value}
        user_info = get_remote(get_config("login.gitcafe.user_info_url"), headers=header)
        log.debug("get user info from GitCafe:" + user_info + "\n")
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
        user_with_token = self.um.db_login(id,
                                           provider=OAUTH_PROVIDER.GITCAFE,
                                           name=name,
                                           nickname=nickname,
                                           access_token=token,
                                           email_info=email_info,
                                           avatar_url=avatar_url)
        return self.user_display_info_with_token(user_with_token)


class WeiboLogin(LoginProviderBase):
    def __init__(self, user_manager):
        self.um = user_manager

    def login(self, args):
        access_token = args.get('access_token')
        uid = args.get('uid')

        # get user info
        # https://api.weibo.com/2/users/show.json?access_token=2.005RDjXC0rYD8d39ca83156aLZWgZE&uid=1404376560
        user_info_resp = get_remote(get_config('login.weibo.user_info_url') + access_token + "&uid=" + uid)
        user_info = json.loads(user_info_resp)
        log.debug("get user base info from Weibo:" + user_info_resp)
        # {"id":2330622122,"idstr":"2330622122","class":1,"screen_name":"test name","name":"test name",
        # "province":"31","city":"10","location":"shanghai yangpu","description":"","url":"",
        # "profile_image_url":"http://tp3.sinaimg.cn/2330622122/50/5629035320/1",
        # "profile_url":"u/2330622122","domain":"","weihao":"","gender":"m","followers_count":34,
        # "friends_count":42,"pagefriends_count":0,"statuses_count":0,"favourites_count":1,
        # "created_at":"Mon Aug 22 17:58:15 +0800 2011","following":false,"allow_all_act_msg":false,
        # "geo_enabled":true,"verified":false,"verified_type":-1,"remark":"","ptype":0,"allow_all_comment":true,
        # "avatar_large":"http://tp3.sinaimg.cn/2330622122/180/5629035320/1","avatar_hd":"http://tp3.sinaimg.cn/2330622122/180/5629035320/1",
        # "verified_reason":"","verified_trade":"","verified_reason_url":"","verified_source":"","verified_source_url":"",
        # "follow_me":false,"online_status":0,"bi_followers_count":8,"lang":"zh-cn","star":0,"mbtype":0,"mbrank":0,
        # "block_word":0,"block_app":0,"credit_score":80,"urank":6}
        openid = user_info['id']
        name = user_info['name']
        nickname = user_info['screen_name']
        avatar_url = user_info['avatar_hd']

        # get user email
        email_info = []
        try:
            email_info_resp = get_remote(get_config('login.weibo.email_info_url') + access_token)
            log.debug("get email from github:" + email_info_resp)
            email_info_resp_json = json.loads(email_info_resp)
            email = email_info_resp_json['email']
            email_info = [
                {'name': name, 'email': email, 'id': openid, 'verified': 1, 'primary': 1, 'nickname': nickname,
                 'avatar_url': avatar_url}]
        except Exception as e:
            log.debug("fail to get user email from weibo")
            log.error(e)

        user_with_token = self.um.db_login(openid,
                                           provider=OAUTH_PROVIDER.WEIBO,
                                           name=name,
                                           nickname=nickname,
                                           access_token=access_token,
                                           email_info=email_info,
                                           avatar_url=avatar_url)
        return self.user_display_info_with_token(user_with_token)


class LiveLogin(LoginProviderBase):
    def __init__(self, user_manager):
        self.um = user_manager

    def login(self, args):
        access_token = args.get('access_token')
        log.debug("access_token is following")
        log.debug(access_token)
        log.debug(get_config('login.live.user_info_url'))

        user_info_resp = get_remote(get_config('login.live.user_info_url') + access_token)
        # conn.request('GET',url,'',{'user-agent':'flask'})
        log.debug("get user info from live:" + user_info_resp)
        # user.info
        # {u'first_name': u'Ice', u'last_name': u'Shi', u'name': u'Ice Shi', u'locale': u'en_US', \
        # u'gender': None,\
        # u'emails': {u'personal': None, u'account': u'iceshi@outlook.com', u'business': None, u'preferred': u'iceshi@outlook.com'}, \
        # u'link': u'https://profile.live.com/', \
        # u'updated_time': u'2015-05-13T02:28:32+0000',\
        # u'id': u'655c03b1b314b5ee'}

        user_info = json.loads(user_info_resp)
        log.debug(user_info)
        name = user_info["name"]
        openid = str(args.get('user_id'))
        # avatar = user_info["avatar_url"]


        email = user_info["emails"]["account"]
        email_info = [
            {'name': name, 'email': email, 'id': openid, 'verified': 1, 'primary': 1, 'nickname': name,
             'avatar_url': None}]
        user_with_token = self.um.db_login(openid,
                                           provider=OAUTH_PROVIDER.LIVE,
                                           name=name,
                                           nickname=name,
                                           access_token=access_token,
                                           email_info=email_info,
                                           avatar_url=None)
        return self.user_display_info_with_token(user_with_token)


login_providers = {
    OAUTH_PROVIDER.GITHUB: GithubLogin(user_manager),
    OAUTH_PROVIDER.QQ: QQLogin(user_manager),
    OAUTH_PROVIDER.GITCAFE: GitcafeLogin(user_manager),
    OAUTH_PROVIDER.WEIBO: WeiboLogin(user_manager),
    OAUTH_PROVIDER.LIVE: LiveLogin(user_manager)
}