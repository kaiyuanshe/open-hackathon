# "javascript" section for javascript. see @app.route('/config.js') in app/views.py

# oauth constants
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
            "user_info_url": 'https://api.github.com/user?access_token=',
            "emails_info_url": 'https://api.github.com/user/emails?access_token='
        },
        "qq": {
            "openid_url": 'https://graph.qq.com/oauth2.0/me?access_token=',
            "user_info_url": 'https://graph.qq.com/user/get_user_info?access_token=%s&oauth_consumer_key=%s&openid=%s'
        },
        "gitcafe": {
            "user_info_url": "https://api.gitcafe.com/api/v1/user"
        },
        "weibo": {
            "user_info_url": 'https://api.weibo.com/2/users/show.json?access_token=',
            "email_info_url": 'https://api.weibo.com/2/account/profile/email.json?access_token='
        },
        "token_expiration_minutes": 60 * 24
    },
    "azure": {
        "subscriptionId": "31e6e137-4656-4f88-96fb-4c997b14a644",
        "certPath": "/home/if/If/LABOSS/open-hackathon/src/hackathon/certificates/1-31e6e137-4656-4f88-96fb-4c997b14a644.pem",
        "managementServiceHostBase": "management.core.chinacloudapi.cn"
    },
    "guacamole": {
        "host": "http://localhost:8080"
    },
    "scheduler": {
        "job_store": "mysql",
        "job_store_url": 'mysql://%s:%s@%s/%s' % (MYSQL_USER, MYSQL_PWD, MYSQL_HOST, MYSQL_DB)
    }
}



