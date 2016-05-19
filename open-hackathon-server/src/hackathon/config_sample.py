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
QQ_OAUTH_STATE = "openhackathon"  # todo state should not be constant. Actually it should be unguessable to prevent CSFA

HACKATHON_SERVER_ENDPOINT = "http://localhost:15000"

MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "hackathon"

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
        "token_valid_time_minutes": 60
    },
    "azure": {
        "cert_base": "",
    },
    "guacamole": {
        "host": "http://localhost:8080"
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
        "azure": {
            "account_name": "",
            "account_key": "",
            "image_container": "images",
            "template_container": "templates",
            "certificates_container": "certificates",
            "user_file_container": "userfile",
            "team_file_container": "teamfile",
            "hack_file_container": "hackfile",
            "blob_service_host_base": ".blob.core.chinacloudapi.cn"
        }
    },
    "docker": {
        "alauda": {
            "token": "",
            "namespace": "",
            "endpoint": "http://api.int.alauda.io",
            "region_name": "BEIJING1"
        }
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
    }
}
