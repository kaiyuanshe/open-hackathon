# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

# DEFAULT ROLES
class ROLE:
    ADMIN = 1
    JUDGE = 2
    USER = 3


class LOGIN_PROVIDER:
    DB = "db"
    GITHUB = "github"
    QQ = "qq"
    WEIBO = "weibo"
    LIVE = "live"
    ALAUDA = "alauda"
    WECHAT = "wechat"


class HTTP_HEADER:
    TOKEN = "token"
    HACKATHON_ID = "hackathon_id"
