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

    def send_emails(self, sender, receivers, subject, content, host, port, username, password,
                    cc=[], bcc=[], attachments=[]):
        """Send emails
        notes: No all email-service providers support.
        if using Gmail, enable "Access for less secure apps" for the sender's account,

        :type sender: str|unicode
        :param sender: Example-'James james2015@gmail.com' or 'james2015@gmail.com'

        :type receivers: list
        :param receivers: Example-['a@gmail.com', 'b@gmail.com']

        :type subject: str|unicode
        :param subject: subject of email's header. Example-'Hello'

        :type content: str|unicode
        :param content: content of the email. Example-'<b>Hi!</b>'

        :type host: str|unicode
        :param host: domain name or ip address. Example-'smtp.gmail.com',

        :type port: integer
        :param port: the port of email service. (SMTP)Example-587

        :type username: str|unicode
        :param username: username to log in the email service. Example-'james@gmail.com'

        :type password: str|unicode
        :param password: password to log in the email service

        :type cc: list
        :param cc: CarbonCopy. Example-['a@gmail.com', 'b@gmail.com']

        :type bcc: list
        :param bcc: BlindCarbonCopy. Example-['a@gmail.com', 'b@gmail.com']

        :type attachments: list
        :param attachments: Example-['C:/Users/Administrator/Downloads/apache-maven-3.3.3-bin.zip']

        :rtype object
        :return 'response' object. response.status_code==250(SMTP) if succeed in sending.
        """
        e = email(
            sender=sender,
            receivers=receivers,
            cc=cc,
            bcc=bcc,
            subject=subject,
            content=content
        )

        postman = Postman(
            host=host,
            port=port,
            middlewares=[
                TLS(force=True),
                Auth(username=username, password=password)
            ]
        )

        response = postman.send(e)
        return response

    def send_template_SMS_by_RongLian(self, to, tempId, datas):
        """ Send template-SMS through RongLian_YunTongXun service

        :type to: integer
        :param to: the telephone number. Example-18217511111

        :type tempId: integer
        :param tempId: SMS-template-Id that would be used, could be editted in RongLian officaial website. Example-1

        :type datas: list
        :param datas: datas to replace blanks in this SMS-template. Example-['10','30']

        :rtype boolean
        :return True if sms sends successfully. False if fails to send.
        """
        serverIP = 'sandboxapp.cloopen.com'
        serverPort = '8883'
        softVersion = '2013-12-26'

        accountSid = self.get_config("sms.rong_lian.account_sid")
        accountToken = self.get_config("sms.rong_lian.account_token")
        appId = self.get_config("sms.rong_lian.app_id")

        if accountSid == "":
            log.error("Send SMS Fail: RongLian_AccountSid is empty")
            return False
        if accountToken == "":
            log.error("Send SMS Fail: RongLian_AccountToken is empty")
            return False
        if appId == "":
            log.error("Send SMS Fail: RongLian_AppId is empty")
            return False

        nowdate = datetime.now().strftime("%Y%m%d%H%M%S")
        signature = accountSid + accountToken + nowdate
        sig = hashlib.md5(signature).hexdigest().upper()
        url = "https://" + serverIP + ":" + serverPort + "/" + softVersion + "/Accounts/" + accountSid +\
              "/SMS/TemplateSMS?sig=" + sig
        auth = base64.encodestring(accountSid + ":" + nowdate).strip()

        # generate request
        req = urllib2.Request(url)
        req.add_header("Accept", "application/json")
        req.add_header("Content-Type", "application/json;charset=utf-8")
        req.add_header("Authorization", auth)

        # generate request-body
        b = '['
        for data in datas:
            b += '"%s",' % (data)
        b += ']'
        body = '''{"to": "%s", "datas": %s, "templateId": "%s", "appId": "%s"}''' % (to, b, tempId, appId)
        req.add_data(body)

        try:
            res = urllib2.urlopen(req)
            data = res.read()
            res.close()
            response = json.loads(data)
            log.info(response)
            # statusCode == "000000" if sends successfully
            return response["statusCode"] == "000000"
        except Exception as e:
            log.error(e)
            return False
