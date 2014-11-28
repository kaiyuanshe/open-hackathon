# "javascript" section for javascript. see @app.route('/config.js') in app/views.py

Config = {
    "javascript": {
        "renren": {
            "clientID": "client_id=7e0932f4c5b34176b0ca1881f5e88562",
            "redirect_url": "redirect_uri=http://osslab.msopentech.cn/renren",
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
            "redirect_url": "redirect_uri=http://osslab.msopentech.cn/google",
            "scope": "scope=https://www.googleapis.com/auth/userinfo.profile+https://www.googleapis.com/auth/userinfo.email",
            "response_type": "response_type=token",
        },
        "qq": {
            "clientID": "client_id=101157515",
            "redirect_uri": "redirect_uri=http://osslab.msopentech.cn/qq",
            "scope": "scope=get_user_info",
            "state": "state=osslab",
            "response_type": "response_type=code",
        },
        "endTime":"2014,11,20,17,05,40"
    },
    "mysql": {
        "connection": 'mysql://%s:%s@%s/%s' % ("root", "fdkiller2011", "localhost", "osslab"),
        "database": "UserInfo"
    },
    "oauth": {
        "github": {
            "url": '/login/oauth/access_token?client_id=0eded406cf0b3f83b181&client_secret=3c81babd71d0cf60db3362261d42b4ce6b199538&redirect_uri=http://osslab.msopentech.cn/github&code='
        },
        "qq": {
            "url": '/oauth2.0/token?grant_type=authorization_code&client_id=101157515&client_secret=018293bdbc15ddfc84306234aa34aa6c&redirect_uri=http://osslab.msopentech.cn/qq&code='
        }
    }
}



