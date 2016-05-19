# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------

# "javascript" section for javascript. see @app.route('/config.js') in app/views.py

# NOTE: all following key/secrets for test purpose.
HOSTNAME = "http://localhost"  # host name of the UI site
# hacking.kaiyuanshe.cn is used for wechat oauth login
# HOSTNAME = "http://hacking.kaiyuanshe.cn"
# HOSTNAME = "http://open-hackathon-dev.chinacloudapp.cn"  # host name of the UI site
# HOSTNAME = "http://hacking.kaiyuanshe.cn"

QQ_OAUTH_STATE = "openhackathon"  # todo state should be constant. Actually it should be unguessable to prevent CSFA
HACKATHON_API_ENDPOINT = "http://localhost:15000"
# HACKATHON_API_ENDPOINT = "http://open-hackathon-dev.chinacloudapp.cn:15000"
# HACKATHON_API_ENDPOINT = "http://hacking.kaiyuanshe.cn:15000"

# github key for `localhost`
GITHUB_CLIENT_ID = "b44f3d47bdeb26b9c4e6"
GITHUB_CLIENT_SECRET = "98de14161c4b2ed3ea7a19787d62cda73b8e292c"

# github oauth key for `open-hackathon-dev.chinacloudapp.cn`
# GITHUB_CLIENT_ID = "b8e407813350f26bf537"
# GITHUB_CLIENT_SECRET = "daa78ae27e13c9f5b4a884bd774cadf2f75a199f"

QQ_CLIENT_ID = "101200890"
QQ_CLIENT_SECRET = "88ad67bd4521c4cc47136854781cb9b5"
QQ_META_CONTENT = "274307566465013314076545663016134754100636"

WECHAT_APP_ID = "wxe75b8aef71c2059f"
WECHAT_SECRET = "4532b90750f4c7bc70fcfbc42d881622"
WECHAT_OAUTH_STATE = "openhackathon"  # NOTE: may be should be same as QQ_OAUTH_STATE?

WEIBO_CLIENT_ID = "479757037"
WEIBO_CLIENT_SECRET = "efc5e75ff8891be37d90b4eaec5c02de"
WEIBO_META_CONTENT = "ae884e09bc02b700"

LIVE_CLIENT_ID = "000000004414E0A6"
LIVE_CLIENT_SECRET = "b4mkfVqjtwHY2wJh0T4tj74lxM5LgAT2"

ALAUDA_CLIENT_ID = "4VR9kzNZVyWcnk9OnAwMuSus7xOOcozJIpic6W6y"
ALAUDA_CLIENT_SECRET = "E5PUL5h9feLlEirec5HQhjIzYecv7vVbEBjWLBkRMoCoFXdvS1PzNmd4AAeNgu4M2AJ87uGnnJaoDLCcDuVxkBoHRWCn6LmfB4SKK1Dty1SkGukkTcZPEk9wpHLSiRQ3"

Config = {
    "environment": "local",
    "app": {
        "secret_key": "secret_key"
    },
    "login": {
        "github": {
            "client_id": GITHUB_CLIENT_ID,
            "access_token_url": 'https://github.com/login/oauth/access_token?client_id=%s&client_secret=%s&redirect_uri=%s/github&code=' % (
                GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, HOSTNAME),
            "user_info_url": 'https://api.github.com/user?access_token=',
            "emails_info_url": 'https://api.github.com/user/emails?access_token='
        },
        "qq": {
            "client_id": QQ_CLIENT_ID,
            "meta_content": QQ_META_CONTENT,
            "access_token_url": 'https://graph.qq.com/oauth2.0/token?grant_type=authorization_code&client_id=%s&client_secret=%s&redirect_uri=%s/qq&code=' % (
                QQ_CLIENT_ID, QQ_CLIENT_SECRET, HOSTNAME),
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
            "access_token_url": 'https://api.weibo.com/oauth2/access_token?client_id=%s&client_secret=%s&grant_type=authorization_code&redirect_uri=%s/weibo&code=' % (
                WEIBO_CLIENT_ID, WEIBO_CLIENT_SECRET, HOSTNAME)
        },
        "live": {
            "client_id": LIVE_CLIENT_ID,
            "client_secret": LIVE_CLIENT_SECRET,
            "redirect_uri": '%s/live' % HOSTNAME,
            "access_token_url": 'https://login.live.com/oauth20_token.srf',
            "user_info_url": 'https://apis.live.net/v5.0/me?access_token='
        },
        "alauda": {
            "client_id": ALAUDA_CLIENT_ID,
            "client_secret": ALAUDA_CLIENT_SECRET,
            "redirect_uri": '%s/alauda' % HOSTNAME,
            "access_token_url": 'http://console.int.alauda.io/oauth/token'
        },
        "provider_enabled": ["github", "wechat"],
        "session_valid_time_minutes": 60
    },
    "hackathon-api": {
        "endpoint": HACKATHON_API_ENDPOINT
    },
    "javascript": {
        "github": {
            "authorize_url": "https://github.com/login/oauth/authorize?client_id=%s&redirect_uri=%s/github&scope=user" % (
                GITHUB_CLIENT_ID, HOSTNAME)
        },
        "weibo": {
            "authorize_url": "https://api.weibo.com/oauth2/authorize?client_id=%s&redirect_uri=%s/weibo&scope=all" % (
                WEIBO_CLIENT_ID, HOSTNAME)
        },
        "qq": {
            "authorize_url": "https://graph.qq.com/oauth2.0/authorize?client_id=%s&redirect_uri=%s/qq&scope=get_user_info&state=%s&response_type=code" % (
                QQ_CLIENT_ID, HOSTNAME, QQ_OAUTH_STATE)
        },
        "wechat": {
            "authorize_url": "https://open.weixin.qq.com/connect/qrconnect?appid=%s&redirect_uri=%s/wechat&response_type=code&scope=snsapi_login&state=%s#wechat_redirect" % (
                WECHAT_APP_ID, HOSTNAME, WECHAT_OAUTH_STATE)
        },
        "live": {
            "authorize_url": "https://login.live.com/oauth20_authorize.srf?client_id=%s&scope=wl.basic+,wl.emails&response_type=code&redirect_uri=%s/live" % (
                LIVE_CLIENT_ID, HOSTNAME)
        },
        "alauda": {
            "authorize_url": "http://console.int.alauda.io/oauth/authorize?response_type=code&client_id=%s&state=state&redirect_uri=%s/alauda" % (
                ALAUDA_CLIENT_ID, HOSTNAME)
        },
        "hackathon": {
            "endpoint": HACKATHON_API_ENDPOINT
        },
        "apiconfig": {
            "proxy": HACKATHON_API_ENDPOINT,
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
                    "azure": {
                        "": ["get", "post", "delete", "put"],
                        "checksubid": ["post"]
                    },
                    "experiment": {
                        "list": ["get"],
                        "": ["post", "put"]
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
                    "template": ["post", "delete"]
                },
                "talent": {
                    "list": ["get"]
                },
                "grantedawards": ["get"]
            }
        }
    }

}
