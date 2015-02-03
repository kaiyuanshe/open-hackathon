# "javascript" section for javascript. see @app.route('/config.js') in app/views.py

# oauth constants
HOSTNAME = "http://osslab.msopentech.cn"
QQ_OAUTH_STATE = "openhackathon"  # todo state should be constant. Actually it should be unguessable to prevent CSFA

MYSQL_HOST = "localhost"
MYSQL_USER = "hackathon"
MYSQL_PWD = "hackathon"
MYSQL_DB = "hackathon"

Config = {
    "environment": "local",
    "mysql": {
        "connection": 'mysql://%s:%s@%s/%s' % (MYSQL_USER, MYSQL_PWD, MYSQL_HOST, MYSQL_DB)
    },
    "login": {
        "github": {
            "access_token_url": 'https://github.com/login/oauth/access_token?client_id=0eded406cf0b3f83b181&client_secret=3c81babd71d0cf60db3362261d42b4ce6b199538&redirect_uri=%s/github&code=' % HOSTNAME,
            "user_info_url": 'https://api.github.com/user?access_token=',
            "emails_info_url": 'https://api.github.com/user/emails?access_token='
        },
        "qq": {
            "access_token_url": 'https://graph.qq.com/oauth2.0/token?grant_type=authorization_code&client_id=101157515&client_secret=018293bdbc15ddfc84306234aa34aa6c&redirect_uri=%s/qq&code=' % HOSTNAME,
            "openid_url": 'https://graph.qq.com/oauth2.0/me?access_token=',
            "user_info_url": 'https://graph.qq.com/user/get_user_info?access_token=%s&oauth_consumer_key=%s&openid=%s'
        },
        "provider_enabled": ["github", "qq"],
        "session_minutes": 60,
        "token_expiration_minutes": 60 * 24
    },
    "register": {
        "limitUnRegisteredUser": False
    },
    "azure": {
        "subscriptionId": "31e6e137-4656-4f88-96fb-4c997b14a644",
        "certPath": "/home/junbo/juni-openhackathon.pem",
        "managementServiceHostBase": "management.core.chinacloudapi.cn"
    },
    "guacamole": {
        "host": "http://locahost:8080"
    }
}



