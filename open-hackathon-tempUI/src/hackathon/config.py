# "javascript" section for javascript. see @app.route('/config.js') in app/views.py

# oauth constants
HOSTNAME = "http://hackathon.chinacloudapp.cn"  # host name of the UI site
QQ_OAUTH_STATE = "openhackathon"  # todo state should be constant. Actually it should be unguessable to prevent CSFA
HACkATHON_API_ENDPOINT = "http://10.86.28.136:15000"

Config = {
    "environment": "local",
    "login": {
        "github": {
            "access_token_url": 'https://github.com/login/oauth/access_token?client_id=a10e2290ed907918d5ab&client_secret=5b240a2a1bed6a6cf806fc2f34eb38a33ce03d75&redirect_uri=%s/github&code=' % HOSTNAME,
            "user_info_url": 'https://api.github.com/user?access_token=',
            "emails_info_url": 'https://api.github.com/user/emails?access_token='
        },
        "qq": {
            "access_token_url": 'https://graph.qq.com/oauth2.0/token?grant_type=authorization_code&client_id=101157515&client_secret=018293bdbc15ddfc84306234aa34aa6c&redirect_uri=%s/qq&code=' % HOSTNAME,
            "openid_url": 'https://graph.qq.com/oauth2.0/me?access_token=',
            "user_info_url": 'https://graph.qq.com/user/get_user_info?access_token=%s&oauth_consumer_key=%s&openid=%s'
        },
        "gitcafe": {
            "access_token_url": 'https://s.gitcafe.org/oauth/token?client_id=3c4db5b888e7cb35e6f580f9eb6777655f228a66d2beaaf361de3578b88fe46e&client_secret=e32af01fe52f5c57312b1ccca4bdead604bb6e6314f66a569a924b9ff6223d74&redirect_uri=%s/gitcafe&grant_type=authorization_code&code=' % HOSTNAME
        },
        "provider_enabled": ["github", "qq", "gitcafe"],
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
        "google": {
            "clientID": "client_id=304944766846-7jt8jbm39f1sj4kf4gtsqspsvtogdmem.apps.googleusercontent.com",
            "redirect_url": "redirect_uri=%s/google" % HOSTNAME,
            "scope": "scope=https://www.googleapis.com/auth/userinfo.profile+https://www.googleapis.com/auth/userinfo.email",
            "response_type": "response_type=token",
        },
        "qq": {
            "clientID": "client_id=101157515",
            "redirect_uri": "redirect_uri=%s/qq" % HOSTNAME,
            "scope": "scope=get_user_info",
            "state": "state=%s" % QQ_OAUTH_STATE,
            "response_type": "response_type=code",
        },
        "gitcafe": {
            "clientID": "client_id=3c4db5b888e7cb35e6f580f9eb6777655f228a66d2beaaf361de3578b88fe46e",
            "clientSecret": "client_secret=e32af01fe52f5c57312b1ccca4bdead604bb6e6314f66a569a924b9ff6223d74",
            "redirect_uri": "redirect_uri=http://hackathon.chinacloudapp.cn/gitcafe",
            "response_type": "response_type=code",
            "code": "d64ee06fe6f0fd4607ac5d9219d2f53c94eba7d4da0d07ddf8960f0b2922e29e",
            "scope": "scope=read"
        },
        "hackathon": {
            "endpoint": HACkATHON_API_ENDPOINT
        }
    }
}



