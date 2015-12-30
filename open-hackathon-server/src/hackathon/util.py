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

import importlib
import json
import os
import hashlib
import base64
import urllib2
from datetime import datetime
from mailthon import email
from mailthon.postman import Postman
from mailthon.middleware import TLS, Auth

from hackathon.log import log
from hackathon.constants import EMAIL_SMTP_STATUSCODE, SMS_RONGLIAN_STATUSCODE, SMS_RONGLIAN_TEMPLATE

try:
    from config import Config
except ImportError:
    from config_sample import Config

__all__ = [
    "get_config",
    "safe_get_config",
    "get_class",
    "load_template",
    "call",
    "get_now",
    "Utility"
]


def get_config(key):
    """Get configured value from configuration file according to specified key

    :type key: str or unicode
    :param key: the search key, separate section with '.'. For example: "mysql.connection"

    :Example:
        get_config("mysql.connection")

    :return configured value if specified key exists else None
    :rtype str or unicode or dict
    """
    ret = Config
    for arg in key.split("."):
        if arg in ret and isinstance(ret, dict):
            ret = ret[arg]
        else:
            return None
    return ret


def safe_get_config(key, default_value):
    """Get configured value from configuration file according to specified key and a default value

    :type key: str | unicode
    :param key: the search key, separate section with '.'. For example: "mysql.connection"

    :type default_value: object
    :param default_value: the default value if specified key cannot be found in configuration file

    :Example:
        safe_get_config("mysql.connection", "mysql://root:root@localhost:3306/db")

    :return configured value if specified key exists else the default value
    :rtype str or unicode or dict
    """
    r = get_config(key)
    return r if r else default_value


def get_class(kls):
    """Get the class object by it's name

    :type kls: str or unicode
    :param kls: the the full name, including module name of class name , of a class obj

    :return the class object
    :rtype classobj

    :Example:
        get_class("hackathon.user.UserManager")

    :raise ModuleException if module cannot be imported
    """
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def load_template(url):
    """Load hackathon template from file into a dict

    :type url: str|unicode
    :param url: the absolute path of the template.

    :return dict indicates a hackathon template
    :rtype dict
    """
    try:
        template = json.load(file(url))
    except Exception as e:
        log.error(e)
        return None
    return template


def call(mdl_cls_func, cls_args, func_args):
    # todo refactoring the call method to use standard hackathon_scheduler
    mdl_name = mdl_cls_func[0]
    cls_name = mdl_cls_func[1]
    func_name = mdl_cls_func[2]
    log.debug('call: mdl_name [%s], cls_name [%s], func_name [%s]' % (mdl_name, cls_name, func_name))
    mdl = importlib.import_module(mdl_name)
    cls = getattr(mdl, cls_name)
    func = getattr(cls(*cls_args), func_name)
    func(*func_args)


def get_now():
    """Return the current local date and time without tzinfo"""
    return datetime.utcnow()  # tzinfo=None


class Utility(object):
    """An utility class for those commonly used methods"""

    def get_now(self):
        """Return the current local date and time without tzinfo"""
        return get_now()

    def convert(self, value):
        """Convert unicode string to str"""
        if isinstance(value, dict):
            return {self.convert(key): self.convert(value) for key, value in value.iteritems()}
        elif isinstance(value, list):
            return [self.convert(element) for element in value]
        elif isinstance(value, unicode):
            return value.encode('utf-8')
        else:
            return value

    def get_config(self, key):
        """Get configured value from configuration file according to specified key

        .. seealso:: get_config outside Utility class
        """
        return get_config(key)

    def safe_get_config(self, key, default_value):
        """Get configured value from configuration file according to specified key and a default value

        .. seealso:: safe_get_config outside Utility class
        """
        return safe_get_config(key, default_value)

    def mkdir_safe(self, path):
        """Create a directory if it doesn't exist

        :return the directory path
        """
        if path and not (os.path.exists(path)):
            os.makedirs(path)
        return path

    def str2bool(self, v):
        if not v:
            return False
        return v.lower() in ["yes", "true", "y", "t", "1"]

    def paginate(self, pagination, func=None):
        """Convert pagination results from DB to serializable dict

        :type pagination: Pagination
        :param pagination: object of Pagination defined in flask-SqlAlchemy

        :type func: function
        :param func: a function that to be applied to each item
        """
        items = pagination.items
        if func:
            items = map(lambda item: func(item), pagination.items)

        return {
            "items": items,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total
        }

    def is_local(self):
        return safe_get_config("environment", "local") == "local"


class Email(object):
    """ Provide Emails Sending Service

    Example for config.py:
    "email": {
        "sender": "James james2015@gmail.com",
        "host": "smtp.gmail.com",
        "port": 587,
        "username": "james2015@gmail.com",
        "password": "88888888"
    }
    """
    sender = safe_get_config("email.sender", "")
    host = safe_get_config("email.host", "")
    port = safe_get_config("email.port", 587)
    username = safe_get_config("email.username", "")
    password = safe_get_config("email.password", "")
    postman = None
    available = False
    error_message = ""

    def __init__(self):
        """check email-service parameters from config.py"""
        if self.sender == "":
            self.error_message = "email-sender is empty"
        elif self.host == "":
            self.error_message = "email-host is empty"
        elif self.username == "":
            self.error_message = "email-username is empty"
        elif self.password == "":
            self.error_message = "email-password is empty"
        else:
            self.available = True
            # initial postman
            self.postman = Postman(
                host=self.host,
                port=self.port,
                middlewares=[
                    TLS(force=True),
                    Auth(username=self.username, password=self.password)
                ]
            )

    def send_emails(self, receivers, subject, content, cc=[], bcc=[], attachments=[]):
        """Send emails
        notes: No all email-service providers support.
        if using Gmail, enable "Access for less secure apps" for the sender's account,

        Examples:
            xxx.send_emails(['receiver1@gmail.com', 'receiver2@gmail.com'],
                            'Subject: Hello',
                            '<b>Hi! Here is the content of email</b>',
                            ['cc1@gmail.com', 'cc2@gmail.com'],
                            ['bcc1@gmail.com', 'bcc2@gmail.com'],
                            ['C:/apache-maven-3.3.3-bin.zip'])

        :type receivers: list
        :param receivers: Example-['a@gmail.com', 'b@gmail.com']

        :type subject: str|unicode
        :param subject: subject of email's header. Example-'Hello'

        :type content: str|unicode
        :param content: content of the email. Example-'<b>Hi!</b>'

        :type cc: list
        :param cc: CarbonCopy. Example-['a@gmail.com', 'b@gmail.com']

        :type bcc: list
        :param bcc: BlindCarbonCopy. Example-['a@gmail.com', 'b@gmail.com']

        :type attachments: list
        :param attachments: Example-['C:/Users/Administrator/Downloads/apache-maven-3.3.3-bin.zip']

        :rtype boolean
        :return True if send emails successfully. False if fails to send.
        """
        if not self.available:
            log.error("Send emails fail: " + self.error_message)
            return False

        e = email(
            sender=self.sender,
            receivers=receivers,
            cc=cc,
            bcc=bcc,
            subject=subject,
            content=content
        )

        try:
            response = self.postman.send(e)
            if response.status_code == EMAIL_SMTP_STATUSCODE.SUCCESS:
                return True
            log.error("Send emails fail: " + response.message)
            return False
        except Exception as e:
            log.error(e)
            return False


class SMS(object):
    """ Provide SMS Sending Service

    Example for config.py:
    "sms": {
        "rong_lian": {
            "account_sid": "aaf98f8951d38e890151d80000000000",
            "auth_token": "81225da0fcab460ea87a3b0000000000",
            "app_id": "8a48b55151d688bc0151d80000000000",
            "server_ip": "sandboxapp.cloopen.com",
            "server_port": "8883",
            "soft_version": "2013-12-26"
        }
    }

    notes: "account_sid, auth_token, app_id" are shown in the RongLianYunTongXun "management console" website.
    """
    account_sid = safe_get_config("sms.rong_lian.account_sid", "")
    auth_token = safe_get_config("sms.rong_lian.auth_token", "")
    app_id = safe_get_config("sms.rong_lian.app_id", "")
    server_ip = safe_get_config("sms.rong_lian.server_ip", "")
    server_port = safe_get_config("sms.rong_lian.server_port", "")
    soft_version = safe_get_config("sms.rong_lian.soft_version", "")
    available = False
    error_message = ""

    def __init__(self):
        """check sms service parameters from config.py"""
        if self.account_sid == "":
            self.error_message = "SMS(RongLian)-account_sid is empty"
        elif self.auth_token == "":
            self.error_message = "SMS(RongLian)-auth_token is empty"
        elif self.app_id == "":
            self.error_message = "SMS(RongLian)-app_id is empty"
        elif self.server_ip == "":
            self.error_message = "SMS(RongLian)-server_ip is empty"
        elif self.server_port == "":
            self.error_message = "SMS(RongLian)-server_port is empty"
        elif self.soft_version == "":
            self.error_message = "SMS(RongLian)-soft_version is empty"
        else:
            self.available = True

    def send_template_SMS_by_RongLian(self, receiver, templateId, datas):
        """ Send template-SMS through RongLian_YunTongXun service

        Example:
            XXX.send_template_SMS_by_RongLian(18217511111,
                                              SMS_RONGLIAN_TEMPLATE.DEFAULT_TEMPLATE,
                                              ['10','30'])

        :type receiver: integer
        :param receiver: the telephone number. Example-18217511111

        :type templateId: integer
        :param templateId: SMS-template-Id that would be used, Example: SMS_RONGLIAN_TEMPLATE.DEFAULT_TEMPLATE

        :type datas: list
        :param datas: datas to replace blanks in this SMS-template. Example-['10','30']

        :rtype boolean
        :return True if sms sends successfully. False if fails to send.
        """

        if not self.available:
            log.error("Send SMS(RongLian) fail: " + self.error_message)
            return False

        # generate sms request
        req = self.__generate_sms_request_RongLian()

        try:
            # generate request-body
            body = {"to": receiver, "datas": datas, "templateId": templateId, "appId": self.app_id}
            req.add_data(str(body))

            res = urllib2.urlopen(req)
            data = res.read()
            res.close()
            response = json.loads(data)
            if response["statusCode"] == SMS_RONGLIAN_STATUSCODE.SUCCESS:
                return True
            log.error("Send SMS(RongLian) fail: " + str(response))
            return False
        except Exception as e:
            log.error(e)
            return False

    def __generate_sms_request_RongLian(self):
        """ private function to generate SMS-request through RongLianYunTongXun-service

        :rtype object(request)
        :return sms-request-object
        """
        nowdate = datetime.now().strftime("%Y%m%d%H%M%S")
        # generate signature
        signature = self.account_sid + self.auth_token + nowdate
        # hash signature
        sig = hashlib.md5(signature).hexdigest().upper()
        url = "https://%s:%s/%s/Accounts/%s/SMS/TemplateSMS?sig=%s" % (self.server_ip, self.server_port,
                                                                       self.soft_version, self.account_sid, sig)
        # auth
        auth = base64.encodestring(self.account_sid + ":" + nowdate).strip()

        # generate request
        req = urllib2.Request(url)
        req.add_header("Accept", "application/json")
        req.add_header("Content-Type", "application/json;charset=utf-8")
        req.add_header("Authorization", auth)

        return req
