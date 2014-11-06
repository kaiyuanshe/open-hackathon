# "javascript" section for javascript. see @app.route('/config.js') in app/views.py

Config = {
    "javascript": {
        "google_ClientID": "client_id=304944766846-7jt8jbm39f1sj4kf4gtsqspsvtogdmem.apps.googleusercontent.com",
        "google_redirect_url": "redirect_uri=http://osslab.msopentech.cn/google",
        "google_scope": "scope=https://www.googleapis.com/auth/userinfo.profile+https://www.googleapis.com/auth/userinfo.email",
        "google_response_type": "response_type=token",
        "github_ClientID": "client_id=0eded406cf0b3f83b181",
        "github_redirect_uri": "redirect_uri=http://osslab.msopentech.cn/github",
        "github_scope": "scope=user",
        "qq_ClientID": "client_id=101157515",
        "qq_redirect_uri": "redirect_uri=http://osslab.msopentech.cn/qq",
        "qq_scope": "scope=get_user_info",
        "qq_state": "state=osslab",
        "qq_response_type": "response_type=code",
        "renren_ClientID": "client_id=7e0932f4c5b34176b0ca1881f5e88562",
        "renren_redirect_url": "redirect_uri=http://osslab.msopentech.cn/renren",
        "renren_scope": "scope=read_user_message+read_user_feed+read_user_photo",
        "renren_response_type": "response_type=token"
    },
    "mysql": {
        "connection": 'mysql://%s:%s@%s/%s' % ("root" , "fdkiller2011", "localhost", "osslab"),
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


