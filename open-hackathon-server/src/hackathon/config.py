# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""
import os

# "javascript" section for javascript. see @app.route('/config.js') in app/views.py

# oauth constants
HACKATHON_SERVER_ENDPOINT = os.environ("HACKATHON_SERVER_ENDPOINT", "http://localhost:15000")

MONGODB_HOST = os.environ("DB_SERVER", "mongo")
MONGODB_PORT = int(os.environ("DB_PORT", "27017"))
MONGODB_DB = os.environ("MONGODB_DB", "hackathon")

GITHUB_CLIENT_ID = os.environ("GITHUB_CLIENT_ID", "b44f3d47bdeb26b9c4e6")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "98de14161c4b2ed3ea7a19787d62cda73b8e292c")

AUTHING_CLIENT_ID = os.environ("AUTHING_CLIENT_ID", "ebfd4eea09a3cf2f6e16")
AUTHING_STATE = os.environ("AUTHING_STATE", "5f0e628e4ba608e9a69533ae")

QQ_CLIENT_ID = os.getenv("QQ_CLIENT_ID", "101200890")
QQ_CLIENT_SECRET = os.getenv("QQ_CLIENT_SECRET", "88ad67bd4521c4cc47136854781cb9b5")
QQ_META_CONTENT = os.getenv("QQ_META_CONTENT", "274307566465013314076545663016134754100636")
QQ_OAUTH_STATE = os.environ("QQ_OAUTH_STATE", "openhackathon")  # todo state should not be constant. Actually it should be unguessable to prevent CSFA


WECHAT_APP_ID = os.getenv("WECHAT_APP_ID", "wxe75b8aef71c2059f")
WECHAT_SECRET = os.getenv("WECHAT_SECRET", "4532b90750f4c7bc70fcfbc42d881622")
WECHAT_OAUTH_STATE = os.getenv("WECHAT_OAUTH_STATE", "openhackathon")  # NOTE: may be should be same as QQ_OAUTH_STATE?

WEIBO_CLIENT_ID = os.getenv("WEIBO_CLIENT_ID", "479757037")
WEIBO_CLIENT_SECRET = os.getenv("WEIBO_CLIENT_SECRET", "efc5e75ff8891be37d90b4eaec5c02de")
WEIBO_META_CONTENT = os.getenv("WEIBO_META_CONTENT", "ae884e09bc02b700")

LIVE_CLIENT_ID = os.getenv("LIVE_CLIENT_ID", "000000004414E0A6")
LIVE_CLIENT_SECRET = os.getenv("LIVE_CLIENT_SECRET", "b4mkfVqjtwHY2wJh0T4tj74lxM5LgAT2")

Config = {
    "environment": "local",
    "endpoint": HACKATHON_SERVER_ENDPOINT,
    "app": {
        "secret_key": "secret_key"
    },
    "mongodb": {
        "database": MONGODB_DB,
        "host": MONGODB_HOST,
        "port": MONGODB_PORT
    },
    "login": {
        "github": {
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "access_token_url": 'https://github.com/login/oauth/access_token',
            "user_info_url": 'https://api.github.com/user',
            "emails_info_url": 'https://api.github.com/user/emails'
        },
        "qq": {
            "client_id": QQ_CLIENT_ID,
            "meta_content": QQ_META_CONTENT,
            "access_token_url": 'https://graph.qq.com/oauth2.0/token?state=openhackathon&grant_type=authorization_code&client_id=%s&client_secret=%s&redirect_uri=%%s&code=%%s' % (
                QQ_CLIENT_ID, QQ_CLIENT_SECRET),
            "openid_url": 'https://graph.qq.com/oauth2.0/me?access_token=',
            "user_info_url": 'https://graph.qq.com/user/get_user_info?access_token=%s&oauth_consumer_key=%s&openid=%s'
        },
        "wechat": {
            "client_id": WECHAT_APP_ID,
            "access_token_url": "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%%s&grant_type=authorization_code" % (
                WECHAT_APP_ID, WECHAT_SECRET),
            "user_info_url": "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s"
        },
        "weibo": {
            "client_id": WEIBO_CLIENT_ID,
            "meta_content": WEIBO_META_CONTENT,
            "user_info_url": 'https://api.weibo.com/2/users/show.json?access_token=',
            "email_info_url": 'https://api.weibo.com/2/account/profile/email.json?access_token=',
            "access_token_url": 'https://api.weibo.com/oauth2/access_token?client_id=%s&client_secret=%s&grant_type=authorization_code&redirect_uri=%%s&code=%%s' % (
                WEIBO_CLIENT_ID, WEIBO_CLIENT_SECRET)
        },
        "live": {
            "client_id": LIVE_CLIENT_ID,
            "client_secret": LIVE_CLIENT_SECRET,
            "access_token_url": 'https://login.live.com/oauth20_token.srf',
            "user_info_url": 'https://apis.live.net/v5.0/me?access_token='
        },
        "token_valid_time_minutes": 60
    },
    "guacamole": {
        "host": "http://" + os.environ["GUACAMOLE"] + ":" + os.environ["GUACAMOLE_PORT"]
    },
    "scheduler": {
        # "job_store": "mysql",
        # "job_store_url": 'mysql://%s:%s@%s:%s/%s' % (MYSQL_USER, MYSQL_PWD, MYSQL_HOST, MYSQL_PORT, MYSQL_DB)
        "job_store": "mongodb",
        "database": MONGODB_DB,
        "collection": "jobs",
        "host": MONGODB_HOST,
        "port": MONGODB_PORT
    },
    "storage": {
        "type": "local",
        "size_limit_kilo_bytes": 5 * 1024,
    },
    "email": {
        "host": "",
        "port": 587,
        "default_sender": "",
        "receivers_forced": [],
        "username": "",
        "password": "",
        "email_templates": {
            "dev_plan_submitted_notify": {
                "title": "开放黑客松: %s 团队开发计划书已提交",
                "default_file_name": "dev_plan_notification.html"
            }
        }
    },
    "voice_verify": {
        "enabled": False,
        "provider": "",
        "rong_lian": {
            "account_sid": "",
            "auth_token": "",
            "app_id": "",
            "server_ip": "https://app.cloopen.com",
            "server_port": "8883",
            "soft_version": "2013-12-26",
            "play_times": 3,
            "display_number": "",
            "response_url": "",
            "language": "zh"
        }
    },
    "sms": {
        "enabled": False,
        "provider": "",
        "china_telecom": {
            "url": "http://api.189.cn/v2/emp/templateSms/sendSms",
            "app_id": "",
            "app_secret": "",
            "url_access_token": "https://oauth.api.189.cn/emp/oauth2/v3/access_token"
        }
    },
    "ukylin": {
        "k8s": {
            "ips": ["119.3.202.71", "49.4.90.39"],
            "template": {
                "name": "Kubernetes",
                "description": "Kubernetes",
                "virtual_environments": [
                    {
                        "images": [
                            {
                                "image": "SOME IMAGE"
                            }
                        ],
                        "cluster": {
                            "token": "SOME TOKEN",
                            "namespace": "default",
                            "api_url": "SOME URL"
                        },
                        "ports": [
                            {
                                "public": True,
                                "public_port": 30006,
                                "protocol": "TCP",
                                "name": "UKylin",
                                "port": 5900
                            }
                        ],
                        "provider": 3,
                        "name": "ukylin"
                    }
                ]
            }
        }
    }
}
