from database import *
from functions import *
from log import log
import json

class QQLogin(object):
    def qq_authorized(self, auth_code, state):
        # get access token
        token_resp = get_remote(get_config("oauth/qq/access_token_url") + auth_code + '&state=' + state)
        log.debug("get token from qq:" + token_resp)
        start = token_resp.index('=')
        end = token_resp.index('&')
        access_token = token_resp[start+1:end]

        # get openID.
        openid_resp = get_remote(get_config("oauth/qq/openid_url") + access_token)
        log.debug("get openid from qq:" + openid_resp)
        info = json.loads(openid_resp[10:-4])
        openid = info['openid']
        client_id = info['client_id']

        # get user info
        url = get_config("oauth/qq/user_info_url") % (access_token, client_id, openid)
        user_info_resp = get_remote(url)
        log.debug("get user info from qq:" + user_info_resp)
        user_info = json.loads(user_info_resp)

        user = User.query.filter_by(openid=openid).first()
        if user is not None:
            user.access_token = access_token
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

        return user

class GithubLogin(object):
    def github_authorized(self, auth_code):
        # get access_token
        token_resp = get_remote(get_config('oauth/github/access_token_url') + auth_code)
        log.debug("get token from github:" + token_resp)
        start = token_resp.index('=')
        end = token_resp.index('&')
        access_token = token_resp[start+1:end]

        # get user info
        user_info_resp = get_remote(get_config('oauth/github/user_info_url') + access_token)
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
        nickname = user_info["name"]
        openid = str(user_info["id"])
        avatar = user_info["avatar_url"]
        email = user_info["email"]

        # todo should we call '/user/emails?access_token=' + access_token to get its primary email?

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

        return user