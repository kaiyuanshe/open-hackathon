# "javascript" section for javascript. see @app.route('/config.js') in app/views.py

# oauth constants
HOSTNAME = "http://hackathon.chinacloudapp.cn"
QQ_OAUTH_STATE = "openhackathon"  # todo state should be constant. Actually it should be unguessable to prevent CSFA
HACkATHON_API_ENDPOINT = "http://hackathon.chinacloudapp.cn/admin"

Config = {
    "environment": "local",
    "mysql": {
        "connection": 'mysql://%s:%s@%s/%s' % ('hackathon', 'hackathon', 'localhost', 'hackathon')
    },
    "login": {
        "github": {
            "access_token_url": 'https://github.com/login/oauth/access_token?client_id=a10e2290ed907918d5ab&client_secret=5b240a2a1bed6a6cf806fc2f34eb38a33ce03d75&redirect_uri=%s/github&code=' % HOSTNAME,
            "user_info_url": 'https://api.github.com/user?access_token=',
            "emails_info_url": 'https://api.github.com/user/emails?access_token='
        },
        "qq": {
            "meta_content": "274307566465013314076545663016134754100636",
            "access_token_url": 'https://graph.qq.com/oauth2.0/token?grant_type=authorization_code&client_id=101192358&client_secret=d94f8e7baee4f03371f52d21c4400cab&redirect_uri=%s/qq&code=' % HOSTNAME,
            "openid_url": 'https://graph.qq.com/oauth2.0/me?access_token=',
            "user_info_url": 'https://graph.qq.com/user/get_user_info?access_token=%s&oauth_consumer_key=%s&openid=%s'
        },
        "weibo":{
            "meta_content": "a6a3b875cfdf95e2",
            "access_token_url": 'https://api.weibo.com/oauth2/access_token?client_id=582725653&client_secret=28f5325cb57613b9f135185b5245c5a2&grant_type=authorization_code&redirect_uri=%s/weibo&code=' % HOSTNAME,
            "user_info_url": 'https://api.weibo.com/2/users/show.json?access_token=',
            "email_info_url": 'https://api.weibo.com/2/account/profile/email.json?access_token='
        },
        "provider_enabled": ["github", "qq"],
        "session_minutes": 60,
        "token_expiration_minutes": 60 * 24
    },
        "hackathon-api": {
        "endpoint": HACkATHON_API_ENDPOINT
    },
    "javascript": {
        "renren": {
            "clientID": "client_id=7e0932f4c5b34176b0ca1881f5e88562",
            "redirect_url": "redirect_uri=%s/renren" % HOSTNAME,
            "scope": "scope=read_user_message+read_user_feed+read_user_photo",
            "response_type": "response_type=token",
        },
        "github": {
            "clientID": "client_id=a10e2290ed907918d5ab",
            "redirect_uri": "redirect_uri=%s/github" % HOSTNAME,
            "scope": "scope=user",
        },
        "weibo": {
            "clientID": "client_id=582725653",
            "redirect_uri": "redirect_uri=%s/weibo" % HOSTNAME,
            "scope": "scope=all",
        },
        "google": {
            "clientID": "client_id=304944766846-7jt8jbm39f1sj4kf4gtsqspsvtogdmem.apps.googleusercontent.com",
            "redirect_url": "redirect_uri=%s/google" % HOSTNAME,
            "scope": "scope=https://www.googleapis.com/auth/userinfo.profile+https://www.googleapis.com/auth/userinfo.email",
            "response_type": "response_type=token",
        },
        "qq": {
            "clientID": "client_id=101192358",
            "redirect_uri": "redirect_uri=%s/qq" % HOSTNAME,
            "scope": "scope=get_user_info",
            "state": "state=%s" % QQ_OAUTH_STATE,
            "response_type": "response_type=code",
        },
        "hackathon": {
            "name": "open-xml-sdk",
            "endpoint": HACkATHON_API_ENDPOINT
        }
    }
}



