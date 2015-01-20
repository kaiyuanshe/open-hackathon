# "javascript" section for javascript. see @app.route('/config.js') in app/views.py

# oauth constants
HOSTNAME = "http://osslab.msopentech.cn"
QQ_OAUTH_STATE = "openhackathon"  # todo state should be constant. Actually it should be unguessable to prevent CSFA

Config = {
    "environment": "local",
    "javascript": {
        "renren": {
            "clientID": "client_id=7e0932f4c5b34176b0ca1881f5e88562",
            "redirect_url": "redirect_uri=%s/renren" % HOSTNAME,
            "scope": "scope=read_user_message+read_user_feed+read_user_photo",
            "response_type": "response_type=token",
        },
        "github": {
            "clientID": "client_id=0eded406cf0b3f83b181",
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
            "redirect_uri": "redirect_uri=http://osslab.msopentech.cn/qq",
            "scope": "scope=get_user_info",
            "state": "state=%s" % QQ_OAUTH_STATE,
            "response_type": "response_type=code",
        },
        "hackathon": {
            "endpoint": HOSTNAME + ":15000"
        }
    }
}



