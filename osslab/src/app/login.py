from database import *
from functions import *
import json

class QQLogin(object):
    def qq_authorized(self, auth_code, state):
        # get access token
        token_resp = get_remote(get_config("oauth/qq/access_token_url") + auth_code + '&state=' + state)
        start = token_resp.index('=')
        end = token_resp.index('&')
        access_token = token_resp[start+1:end]

        # get openID.
        openid_resp = get_remote(get_config("oauth/qq/openid_url") + access_token)
        info = json.loads(openid_resp[10:-4])
        openid = info['openid']
        client_id = info['client_id']

        # get user info
        url = get_config("oauth/qq/user_info_url") % (access_token, client_id, openid)
        user_info = json.loads(get_remote(url))

        user = User.query.filter_by(openid=openid).first()
        if user is not None:
            user.access_token = access_token
            user.name = user_info["nickname"]
            user.avatar_url = user_info["figureurl"]
            user.last_login_time = datetime.utcnow()
            db.session.commit()
        else:
            user = User(user_info["nickname"],
                    None,
                    openid,
                    user_info["figureurl"],
                    access_token)
            db.session.add(user)
            db.session.commit()

        return user