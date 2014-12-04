# "javascript" section for javascript. see @app.route('/config.js') in app/views.py

from constants import *

# oauth constants
HOSTNAME = "http://osslab.msopentech.cn"

Config = {
    "javascript": {
        "renren": {
            "clientID": "client_id=7e0932f4c5b34176b0ca1881f5e88562",
            "redirect_url": "redirect_uri=%s/renren" % HOSTNAME,
            "scope": "scope=read_user_message+read_user_feed+read_user_photo",
            "response_type": "response_type=token",
        },
        "github": {
            "clientID": "client_id=0eded406cf0b3f83b181",
            "redirect_uri": "redirect_uri=http://osslab.msopentech.cn/github",
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
            "redirect_uri": "redirect_uri=http://osslab.msopentech.cn/qq",
            "scope": "scope=get_user_info",
            "state": "state=%s" % QQ_OAUTH_STATE,
            "response_type": "response_type=code",
        },
        "endTime":"2014-11,20,17,05,40"
    },
    "mysql": {
        "connection": 'mysql://%s:%s@%s/%s' % ("hackathon", "hackathon", "localhost", "hackathon"),
        "database": "hackathon"
    },
    "oauth": {
        "github": {
            "access_token_url": 'https://github.com/login/oauth/access_token?client_id=0eded406cf0b3f83b181&client_secret=3c81babd71d0cf60db3362261d42b4ce6b199538&redirect_uri=%s/github&code=' % HOSTNAME,
            "user_info_url": 'https://api.github.com/user?access_token='
        },
        "qq": {
            "access_token_url": 'https://graph.qq.com/oauth2.0/token?grant_type=authorization_code&client_id=101157515&client_secret=018293bdbc15ddfc84306234aa34aa6c&redirect_uri=%s/qq&code=' % HOSTNAME,
            "openid_url": 'https://graph.qq.com/oauth2.0/me?access_token=',
            "user_info_url": 'https://graph.qq.com/user/get_user_info?access_token=%s&oauth_consumer_key=%s&openid=%s'
        }
    },
    "user": {
        "limitUnRegisteredUser": True
    },
    "azure": {
        "subscriptionId": "31e6e137-4656-4f88-96fb-4c997b14a644",
        "certPath": "/home/junbo/juni-osslab.pem",
        "managementServiceHostBase": "management.core.chinacloudapi.cn"
    }
}



