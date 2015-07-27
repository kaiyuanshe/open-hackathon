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

__author__ = 'root'

import sys
import urllib2

sys.path.append("..")

from client.functions import get_remote, get_config, post_to_remote, convert
from client.log import log
import json
import requests
from user_mgr import user_manager
from flask import session, request
from flask_login import logout_user
from client.constants import LOGIN_PROVIDER


class LoginBase():
    def logout(self, admin):
        if admin.is_authenticated():
            if user_manager.db_logout(admin):
                info = "ok"
            else:
                info = "log out failed"
            session.pop("token")
            logout_user()
            return info
        else:
            return "ok"


class QQLogin(LoginBase):
    def login(self, args):
        log.info('login from QQ')
        code = args.get('code')
        state = "openhackathon"
        # if state != QQ_OAUTH_STATE:
        # log.warn("STATE match fail. Potentially CSFR.")
        # return "UnAuthorized", 401

        # get access token
        token_resp = get_remote(get_config("login.qq.access_token_url") + code + '&state=' + state)
        log.debug("get token from qq:" + token_resp)
        start = token_resp.index('=')
        end = token_resp.index('&')
        access_token = token_resp[start + 1:end]
        # get user info
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
        email_list = []

        return user_manager.oauth_db_login(openid,
                                           name=user_info["nickname"],
                                           provider=LOGIN_PROVIDER.QQ,
                                           nickname=user_info["nickname"],
                                           access_token=access_token,
                                           email_list=email_list,
                                           avatar_url=user_info["figureurl"])


class GithubLogin(LoginBase):
    def login(self, args):
        log.info('login from GitHub')
        code = args.get('code')

        # get access_token
        token_resp = get_remote(get_config('login.github.access_token_url') + str(code))
        log.debug("get token from github:" + token_resp)
        start = token_resp.index('=')
        end = token_resp.index('&')
        access_token = token_resp[start + 1:end]
        log.debug("get token info from github")

        # get user info
        user_info_resp = get_remote(get_config('login.github.user_info_url') + access_token)

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
        email_info_resp = get_remote(get_config('login.github.emails_info_url') + access_token)
        log.debug("get email from github:" + email_info_resp + '\n')
        # email_info include all user email provided by github
        # email is user's primary email
        email_list = json.loads(email_info_resp)

        return user_manager.oauth_db_login(openid,
                                           provider=LOGIN_PROVIDER.GITHUB,
                                           name=name,
                                           nickname=nickname,
                                           access_token=access_token,
                                           email_list=email_list,
                                           avatar_url=avatar)


class GitcafeLogin(LoginBase):
    def login(self, args):
        log.info('login from Gitcafe')
        code = args.get('code')
        url = get_config('login.gitcafe.access_token_url') + code
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url, "")
        resp = opener.open(request)
        token_resp = json.loads(resp.read())

        token = token_resp['access_token']
        value = "Bearer " + token
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(get_config("login.gitcafe.user_info_url"))
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
        email_list = [
            {
                'name': name,
                'email': email,
                'verified': 1,
                'primary': 1
            }
        ]

        return user_manager.oauth_db_login(id,
                                           provider=LOGIN_PROVIDER.GITCAFE,
                                           name=name,
                                           nickname=nickname,
                                           access_token=token,
                                           email_list=email_list,
                                           avatar_url=avatar_url)


class WeiboLogin(LoginBase):
    def login(self, args):
        log.info('login from Weibo Sina')
        code = args.get('code')

        # get access_token
        log.debug(get_config('login.weibo.access_token_url') + code)
        token_resp = post_to_remote(get_config('login.weibo.access_token_url') + code, {})
        log.debug("get token from Weibo:" + str(token_resp))

        access_token = token_resp['access_token']
        uid = token_resp['uid']
        log.debug("get token info from Weibo :" + access_token)

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
        avatar = user_info['avatar_hd']

        # get user primary email
        email_info_resp = get_remote(get_config('login.weibo.email_info_url') + access_token)
        log.debug("get email from github:" + email_info_resp)

        email_info_resp_json = json.loads(email_info_resp)
        email = email_info_resp_json['email']

        email_list = [
            {
                'name': name,
                'email': email,
                'verified': 1,
                'primary': 1
            }
        ]

        return user_manager.oauth_db_login(openid,
                                           provider=LOGIN_PROVIDER.WEIBO,
                                           name=name,
                                           nickname=nickname,
                                           access_token=access_token,
                                           email_list=email_list,
                                           avatar_url=avatar)


class MySQLLogin(LoginBase):
    def login(self, args):
        user = request.form['username']
        pwd = request.form['password']
        if user is None or pwd is None:
            log.warn("login without user or pwd")
            return None

        return user_manager.mysql_login(user, pwd)


class LiveLogin(LoginBase):
    def login(self, args):
        log.info('login from  Live')
        code = args.get('code')
        # live need post a form to get token
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        data = {
            'client_id': get_config('login.live.client_id'),
            'client_secret': get_config('login.live.client_secret'),
            'redirect_uri': get_config('login.live.redirect_uri'),
            'grant_type': 'authorization_code',
            'code': code
        }
        # Following is use urllib to post request
        url = get_config('login.live.access_token_url')
        r = requests.post(url, data=data, headers=headers)
        resp = r.json()
        access_token = resp['access_token']
        # example r.text
        # {"token_type":"bearer","expires_in":3600,"scope":"wl.basic wl.emails",
        # "access_token":"EwBwAq1DBAAUGCCXc8wU/zFu9QnLdZXy+YnElFkAAQSgubm26ZSGbRJNqyaoao186USLUXxbkzgPa1GAkyNbv0BOl72kv
        # qz8f81dPGWNowxXQf73gnKkgCIhypqjJqyBzL0+T0z437WhIr6vHW9gtEtMtP8s+ntXMinlbmBbGwjweEL/BA2eu3HapWti097/eF+yo8b/rP
        # KitwOCuCtkamv5N7FM8asZOYkgFlLS1641zuPfOiw/Rz+ijxJj+yc5mPMDAnyr8sGy596VIK2xqeVbZXg5BShAQw+F2GO2udE9ZDF2NgIegFy
        # SRpI3qSDp0Tu8ktPxQSp1lxjb1kQtjmEutdbOU3jjeFZietJTqF/+/NHUUfMwqNycFPv39I0DZgAACCt7Cq2fjA4jQAGV2Ru//g/KrJ4mIF80
        # nvRh70cTfL12Ri0LO9w+GuEJ0QkRZ/JjtZxQXPgRT4KGohO2d7X0sN1a19PEfMng/KwYgEBXbNqkHu/qAwdC4HbAUOnC6bJXESFInbSSu4GKp
        # 02wIRk6cp8x6HV9xCTCs9eXwWEdRH/6kPGSdGnGMZlX3fMWk+xRgwKdy3VSoUtyKHZ3iM/fr4wDpEqmzBXKbzd1crlHe984UvQseeH1nBrG/B
        # ytJ34KXBc12QASUIYCYz43OFp+WAQUmUFyjeHyZSD9jakjJ7raIlWtMeR2cCuhfrkqfmMvoebKqVW1JTR1FV+RfW/WBYRzX/rjJD7StVLVYzN
        # kLTKHotMZ2KQYtN4P/qoN62RWD5w8RC+XpRISUQ6zQo2qg3NeznutrDJNPVwMnmRKMuD7q/hGajFsWX6pi1sB",
        # "user_id":"ffe24352ffeeef16bbab7dfd9819f5ed"}
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

        email = user_info["emails"]["account"]
        email_list = [
            {
                'name': name,
                'email': email,
                'verified': 1,
                'primary': 1
            }
        ]
        return admin_manager.oauth_db_login(openid,
                                            name=name,
                                            nickname=name,
                                            access_token=access_token,
                                            email_info=email_list,
                                            avatar_url=None)


login_providers = {
    LOGIN_PROVIDER.GITHUB: GithubLogin(),
    LOGIN_PROVIDER.WEIBO: WeiboLogin(),
    LOGIN_PROVIDER.QQ: QQLogin(),
    LOGIN_PROVIDER.GITCAFE: GitcafeLogin(),
    LOGIN_PROVIDER.MYSQL: MySQLLogin(),
    LOGIN_PROVIDER.LIVE: LiveLogin()
}
