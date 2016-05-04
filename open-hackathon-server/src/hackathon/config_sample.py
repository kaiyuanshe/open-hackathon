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
        "token_expiration_seconds": 60 * 60
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
                "sub_content": """
                        <tr><td style='padding: 0px; border-collapse: collapse; padding: 10px 20px'><table cellspacing='0' cellpadding='0' border='0' style='border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt'><tbody>
                        <tr>
                            <td valign='middle' style='padding: 0px; border-collapse: collapse; vertical-align: middle; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 1px'> <a href='http://hacking.kaiyuanshe.cn/site/{{hackathon_name}}/team/{{team_id}}' style='color:#3b73af;; color: #3b73af; text-decoration: none'>{{team_name}}</a> 团队开发计划书已提交 </td></tr></tbody></table></td></tr>
                        <tr><td style='padding: 0px; border-collapse: collapse; padding: 0 20px'><table cellspacing='0' cellpadding='0' border='0' width='100%' style='border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; border-spacing: 0; border-collapse: separate'><tbody><tr>
                            <td style='padding: 0px; border-collapse: collapse; color: #ffffff; padding: 0 15px 0 16px; height: 15px; background-color: #ffffff; border-left: 1px solid #cccccc; border-top: 1px solid #cccccc; border-right: 1px solid #cccccc; border-bottom: 0; border-top-right-radius: 5px; border-top-left-radius: 5px; height: 10px; line-height: 10px; padding: 0 15px 0 16px; mso-line-height-rule: exactly' height='10' bgcolor='#ffffff'>&nbsp;</td></tr>
                        <tr><td style='padding: 0px; border-collapse: collapse; border-left: 1px solid #cccccc; border-right: 1px solid #cccccc; border-top: 0; border-bottom: 0; padding: 0 15px 0 16px; background-color: #ffffff' bgcolor='#ffffff'><table cellspacing='0' cellpadding='0' border='0' width='100%' style='border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt'><tbody>
                        <tr><td style='padding: 0px; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px; padding-top: 10px'><a href='http://hacking.kaiyuanshe.cn/index' style='color: #3b73af; text-decoration: none'>Open-hackathon</a> / <a style='color: #3b73af; text-decoration: none'></a> <a href='http://hacking.kaiyuanshe.cn/site/{{hackathon_name}}/team/{{team_id}}' style='color: #3b73af; text-decoration: none'>开发计划书提交通知</a></td></tr>
                            <tr><td style='vertical-align: top;; padding: 0px; border-collapse: collapse; padding-right: 5px; font-size: 20px; line-height: 30px; mso-line-height-rule: exactly'> <span style='font-family: Arial, sans-serif; padding: 0; font-size: 20px; line-height: 30px; mso-text-raise: 2px; mso-line-height-rule: exactly; vertical-align: middle'> <a href='http://hacking.kaiyuanshe.cn/site/{{hackathon_name}}/team/{{team_id}}' style='color: #3b73af; text-decoration: none'>{{team_name}} submitted a dev-plan for {{hackathon_name}}</a> </span> </td></tr></tbody></table></td></tr>
                            <tr><td style='border-collapse: collapse; border-left: 1px solid #cccccc; border-right: 1px solid #cccccc; border-top: 0; border-bottom: 0; padding: 0px 15px 0px 30px; background-color: #ffffff' bgcolor='#ffffff'><table style='border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt'><tbody><tr>
                                    <th style='color: #707070; font: normal 14px/20px Arial, sans-serif; text-align: left; vertical-align: top; padding: 2px 0'><strong>团队名称:</strong></th>
                                    <td style='padding: 0px; border-collapse: collapse; font: normal 14px/20px Arial, sans-serif; padding: 2px 0 2px 5px; vertical-align: top'> <a href='http://hacking.kaiyuanshe.cn/site/{{hackathon_name}}/team/{{team_id}}' style='color:#3b73af; text-decoration: none'>{{team_name}}</a></td>
                                </tr><tr>
                                    <th style='color: #707070; font: normal 14px/20px Arial, sans-serif; text-align: left; vertical-align: top; padding: 2px 0'><strong>活动名称:</strong></th>
                                    <td style='padding: 0px; border-collapse: collapse; font: normal 14px/20px Arial, sans-serif; padding: 2px 0 2px 5px; vertical-align: top'> <a href='http://hacking.kaiyuanshe.cn/site/{{hackathon_name}}' style='color:#3b73af; text-decoration: none'>{{hackathon_name}}</a></td>
                                </tr><tr>
                                    <th style='color: #707070; font: normal 14px/20px Arial, sans-serif; text-align: left; vertical-align: top; padding: 2px 0'><strong>查看计划书:</strong></th>
                                    <td style='padding: 0px; border-collapse: collapse; font: normal 14px/20px Arial, sans-serif; padding: 2px 0 2px 5px; vertical-align: top'> <a href='http://hacking.kaiyuanshe.cn/site/{{hackathon_name}}/team/{{team_id}}' style='background-color:#ddfade; color:#000000; text-decoration: none'><strong>Click here to view the dev-plan detail</strong></a></td>
                                </tr></tbody></table></td></tr>
                            <tr><td style='padding: 0px; border-collapse: collapse; border-left: 1px solid #cccccc; border-right: 1px solid #cccccc; border-top: 0; border-bottom: 0; padding: 0 15px 0 16px; background-color: #ffffff' bgcolor='#ffffff'><table cellspacing='0' cellpadding='0' border='0' width='100%' style='border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 1px'><tbody><tr>
                            <td valign='middle' style='padding: 0px; border-collapse: collapse; padding: 10px 0 10px 24px; vertical-align: middle; padding-left: 0'><table align='left' style='border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt'><tbody>
                                <tr>
                                    <td style='padding: 0px; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 0px; vertical-align: middle'> <a href='http://www.kaiyuanshe.cn/' target='_blank' style='color: #3b73af; text-decoration: none'></a> </td>
                                    <td style='padding: 0px; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 4px; padding-left: 5px'> </td>
                                </tr></tbody></table></td></tr></tbody></table></td></tr>
                                <tr><td style='padding: 0px; border-collapse: collapse; color: #ffffff; padding: 0 15px 0 16px; height: 5px; line-height: 5px; background-color: #ffffff; border-top: 0; border-left: 1px solid #cccccc; border-bottom: 1px solid #cccccc; border-right: 1px solid #cccccc; border-bottom-right-radius: 5px; border-bottom-left-radius: 5px; mso-line-height-rule: exactly' height='5' bgcolor='#ffffff'>&nbsp;</td></tr></tbody></table> </td></tr>
                    """
            },
            "default_template": """
                    <!DOCTYPE html><html>
                    <head><meta http-equiv='Content-Type' content='text/html; charset=UTF-8'/></head>
                    <body style='color: #333333; font-family: Arial, sans-serif; font-size: 14px; line-height: 1.429'>
                        <table cellpadding='0' cellspacing='0' width='100%' style='border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #f5f5f5; border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt' bgcolor='#f5f5f5'>
                            <tbody>
                            {{sub_body}}
                            <tr><td style='padding: 0px; border-collapse: collapse; padding: 12px 20px'>
                                <table cellspacing='0' cellpadding='0' border='0' style='border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt'>
                                    <tbody><tr><td width='100%' style='padding: 0px; border-collapse: collapse; color: #999999; font-size: 12px; line-height: 18px; font-family: Arial, sans-serif; mso-line-height-rule: exactly; mso-text-raise: 2px'> This message was sent by 开源社 <span>(<span>open-hackathon 开放黑客松平台</span>)</span> </td></tr></tbody>
                                </table></td>
                            </tr></tbody></table></body></html>
                """
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
