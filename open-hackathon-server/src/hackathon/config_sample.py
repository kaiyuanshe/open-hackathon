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

# oauth constants
QQ_OAUTH_STATE = "openhackathon"  # todo state should be constant. Actually it should be unguessable to prevent CSFA

MYSQL_HOST = "localhost"
MYSQL_USER = "hackathon"
MYSQL_PWD = "hackathon"
MYSQL_DB = "hackathon"
MYSQL_PORT = 3306

Config = {
    "environment": "local",
    "app": {
        "secret_key": "secret_key"
    },
    "mysql": {
        "connection": 'mysql://%s:%s@%s:%s/%s' % (MYSQL_USER, MYSQL_PWD, MYSQL_HOST, MYSQL_PORT, MYSQL_DB)
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
            # gitcafe domain:  gcas.dgz.sh/gcs.dgz.sh for Staging, api.gitcafe.com/gitcafe.com for Production
            "user_info_url": "https://gcas.dgz.sh/api/v1/user"
        },
        "weibo": {
            "user_info_url": 'https://api.weibo.com/2/users/show.json?access_token=',
            "email_info_url": 'https://api.weibo.com/2/account/profile/email.json?access_token='
        },
        "live": {
            "user_info_url": 'https://apis.live.net/v5.0/me?access_token='
        },
        "token_expiration_minutes": 60 * 24
    },
    "azure": {
        "cert_base": "/home/if/If/open-hackathon/open-hackathon/src/hackathon/certificates",
        "container_name": "certificates"
    },
    "guacamole": {
        "host": "http://localhost:8080"
    },
    "scheduler": {
        "job_store": "mysql",
        "job_store_url": 'mysql://%s:%s@%s:%s/%s' % (MYSQL_USER, MYSQL_PWD, MYSQL_HOST, MYSQL_PORT, MYSQL_DB)
    },
    "pre_allocate": {
        "check_interval_minutes": 5,
        "azure": 1,
        "docker": 1
    },
    "recycle": {
        "idle_hours": 24,
        "check_idle_interval_minutes": 5
    },
    "storage": {
        "account_name": "hackathon",
        "account_key": "U4/oE3Ocwk9txQHw2qNOCCW2Fy05FBY3yQfzcKRNss5tnReyYTO7PDyeXQ8TWMMxXF07JrW7UXPyOhGgJlodEQ==",
        "image_container": "images",
        "template_container": "templates",
        "blob_service_host_base": ".blob.core.chinacloudapi.cn",
        "size_limit_kilo_bytes": 5 * 1024
    },
    "docker": {
        "alauda": {
            "token": "",
            "namespace": "",
            "endpoint": "https://api.alauda.cn"
        }
    },
    "cloud_eclipse": {
        "api": "http://www.idehub.cn/api/ide"
    }
}
