# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

# "javascript" section for javascript. see @app.route('/config.js') in app/views.py

# NOTE: all following key/secrets for test purpose.
ENDPOINT_WEB = "http://localhost"  # host name of the UI site
ENDPOINT_HACKATHON_API = "http://localhost:15000"

GITHUB_CLIENT_ID = "b44f3d47bdeb26b9c4e6"
QQ_CLIENT_ID = "101200890"
QQ_OAUTH_STATE = "openhackathon"  # todo state should be constant. Actually it should be unguessable to prevent CSFA
WECHAT_APP_ID = "wxe75b8aef71c2059f"
WECHAT_OAUTH_STATE = "openhackathon"  # NOTE: may be should be same as QQ_OAUTH_STATE?
WEIBO_CLIENT_ID = "479757037"
LIVE_CLIENT_ID = "000000004414E0A6"

Config = {
    "environment": "local",
    "app": {
        "secret_key": "secret_key"
    },
    "login": {
        "provider_enabled": ["github", "wechat"],
        "session_valid_time_minutes": 60
    },
    "endpoint": {
        "hackathon_web": ENDPOINT_WEB,
        "hackathon_api": ENDPOINT_HACKATHON_API
    },
    "javascript": {
        "github": {
            "authorize_url": "https://github.com/login/oauth/authorize?client_id=%s&scope=user" % (
                GITHUB_CLIENT_ID)
        },
        "weibo": {
            "authorize_url": "https://api.weibo.com/oauth2/authorize?client_id=%s&redirect_uri=%s/weibo&scope=all" % (
                WEIBO_CLIENT_ID, ENDPOINT_WEB)
        },
        "qq": {
            "authorize_url": "https://graph.qq.com/oauth2.0/authorize?client_id=%s&redirect_uri=%s/qq&scope=get_user_info&state=%s&response_type=code" % (
                QQ_CLIENT_ID, ENDPOINT_WEB, QQ_OAUTH_STATE)
        },
        "wechat": {
            "authorize_url": "https://open.weixin.qq.com/connect/qrconnect?appid=%s&redirect_uri=%s/wechat&response_type=code&scope=snsapi_login&state=%s#wechat_redirect" % (
                WECHAT_APP_ID, ENDPOINT_WEB, WECHAT_OAUTH_STATE)
        },
        "wechat_mobile": {
            "authorize_url": "https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s/wechat&response_type=code&scope=snsapi_base&state=%s#wechat_redirect" % (
                WECHAT_APP_ID, ENDPOINT_WEB, WECHAT_OAUTH_STATE)
        },
        "live": {
            "authorize_url": "https://login.live.com/oauth20_authorize.srf?client_id=%s&scope=wl.basic+,wl.emails&response_type=code&redirect_uri=%s/live" % (
                LIVE_CLIENT_ID, ENDPOINT_WEB)
        },
        "hackathon": {
            "endpoint": ENDPOINT_HACKATHON_API
        },
        "apiconfig": {
            "proxy": ENDPOINT_HACKATHON_API,
            "api": {
                "admin": {
                    "hackathon": {
                        "": ["get", "post", "put", "delete"],
                        "checkname": ["get"],
                        "list": ["get"],
                        "online": ["post"],
                        "applyonline": ["post"],
                        "offline": ["post"],
                        "tags": ["get", "post", "put", "delete"],
                        "config": ["get", "post", "put", "delete"],
                        "administrator": {
                            "": ["put", "post", "delete"],
                            "list": ["get"]
                        },
                        "template": {
                            "": ["post", "delete"],
                            "list": ["get"],
                            "check": ["get"]
                        },
                        "organizer": {
                            "": ["get", "post", "put", "delete"]
                        },
                        "award": {
                            "": ["get", "post", "put", "delete"],
                            "list": ["get"]
                        },
                        "notice": {
                            "": ["get", "post", "put", "delete"]
                        }
                    },
                    "registration": {
                        "": ["get", "post", "delete", "put"],
                        "list": ["get"]
                    },
                    "experiment": {
                        "list": ["get"],
                        "": ["post", "put", "delete"]
                    },
                    "team": {
                        "list": ["get"],
                        "score": {
                            "list": ["get"]
                        },
                        "award": ["get", "post", "delete"]
                    },
                    "user": {
                        "list": ["get"]
                    },
                    "hostserver": {
                        "": ["get", "post", "delete", "put"],
                        "list": ["get"]
                    }
                },
                "template": {
                    "": ["get", "post", "delete", "put"],
                    "file": ["post"],
                    "list": ["get"],
                    "check": ["get"]
                },
                "user": {
                    "": ["get"],
                    "login": ["post", "delete"],
                    "experiment": {
                        "": ["get", "post", "delete", "put"]
                    },
                    "registration": {
                        "": ["put", "post", "get"],
                        "checkemail": ["get"],
                        "list": ["get"]
                    },
                    "profile": {
                        "": ["post", "put"]
                    },
                    "picture": {
                        "": ["put"]
                    },
                    "team": {
                        "member": ["get"]
                    },
                    "hackathon": {
                        "like": ["get", "post", "delete"]
                    },
                    "notice": {
                        "read": ["put"]
                    },
                    "show": {
                        "list": ["get"]
                    },
                    "file": {
                        "": ["post"]
                    }
                },
                "hackathon": {
                    "": ["get"],
                    "list": ["get"],
                    "stat": ["get"],
                    "template": ["get"],
                    "team": {
                        "list": ["get"]
                    },
                    "registration": {
                        "list": ["get"]
                    },
                    "show": {
                        "list": ["get"]
                    },
                    "grantedawards": ["get"],
                    "notice": {
                        "list": ["get"]
                    }
                },
                "team": {
                    "": ["get", "post", "put", "delete"],
                    "score": ["get", "post", "put"],
                    "member": {
                        "": ["post", "put", "delete"],
                        "list": ["get"]
                    },
                    "show": ["get", "post", "delete"],
                    "template": ["post", "delete"],
                    "email": ["put"]
                },
                "talent": {
                    "list": ["get"]
                },
                "grantedawards": ["get"]
            }
        }
    }
}
