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
import urllib
import urllib2
import abc
from uuid import UUID
from datetime import datetime, timedelta

from mailthon import email
from mailthon.postman import Postman
from mailthon.middleware import TLS, Auth
from bson import ObjectId

from hackathon_factory import RequiredFeature
from hackathon.log import log
from hackathon.constants import EMAIL_SMTP_STATUSCODE, VOICEVERIFY_RONGLIAN_STATUSCODE, SMS_CHINATELECOM_TEMPLATE, \
    SMS_CHINATELECOM_STATUSCODE, CHINATELECOM_ACCESS_TOKEN_STATUSCODE

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
    "Utility",
    "Email",
    "DisabledVoiceVerify",
    "RonglianVoiceVerify",
    "DisabledSms",
    "ChinaTelecomSms",
    "make_serializable",
]


def make_serializable(item):
    """make an object serializable before saving DB or respond with HTTP"""
    if isinstance(item, list):
        return [make_serializable(sub) for sub in item]
    elif isinstance(item, dict):
        for k, v in item.items():
            item[k] = make_serializable(v)
        return item
    elif isinstance(item, datetime):
        item = item.replace(tzinfo=None)
        epoch = datetime.utcfromtimestamp(0)
        return long((item - epoch).total_seconds() * 1000)
    elif isinstance(item, ObjectId) or isinstance(item, UUID):
        return str(item)
    else:
        return item


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

    def make_serializable(self, v):
        return make_serializable(v)

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

    def send_emails(self, sender, receivers, subject, content, cc=[], bcc=[], attachments=[]):
        email_service = RequiredFeature("email")
        return email_service.send_emails(sender, receivers, subject, content, cc, bcc, attachments)

    def send_voice_verify(self, receiver, content):
        voice_verify_service = RequiredFeature("voice_verify")
        return voice_verify_service.send_voice_verify(receiver, content)

    def send_sms(self, receiver, template_id, content):
        sms_service = RequiredFeature("sms")
        return sms_service.send_sms(receiver, template_id, content)


class Email(object):
    """ Provide Emails Sending Service

    Example for config.py:
    "email": {
        "host": "smtp.gmail.com",
        "port": 587,
        "username": "james2015@gmail.com",
        "password": "88888888"
    }
    """
    available = False

    host = safe_get_config("email.host", "")
    port = safe_get_config("email.port", 587)
    username = safe_get_config("email.username", "")
    password = safe_get_config("email.password", "")
    postman = None
    error_message = ""

    def __init__(self):
        """check email-service parameters from config.py"""
        if self.host == "":
            self.error_message = "Email Error: host is empty"
        elif self.username == "":
            self.error_message = "Email Error: username is empty"
        elif self.password == "":
            self.error_message = "Email Error: password is empty"
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

    def send_emails(self, sender, receivers, subject, content, cc=[], bcc=[], attachments=[]):
        """Send emails
        notes: No all email-service providers support.
        if using Gmail, enable "Access for less secure apps" for the sender's account,

        Examples:
            xxx.send_emails("James jame2015@gmail.com",
                            ['receiver1@gmail.com', 'receiver2@gmail.com'],
                            'Subject: Hello',
                            '<b>Hi! Here is the content of email</b>',
                            ['cc1@gmail.com', 'cc2@gmail.com'],
                            ['bcc1@gmail.com', 'bcc2@gmail.com'],
                            ['C:/apache-maven-3.3.3-bin.zip'])

        :type sender: str|unicode
        :param sender: the nickname and email address of sender. Example:"James jame2015@gmail.com"

        :type receivers: list
        :param receivers: receivers' emails address. Example:['a@gmail.com', 'b@gmail.com']

        :type subject: str|unicode
        :param subject: subject of email's header. Example:'Hello'

        :type content: str|unicode
        :param content: content of the email. Example:'<b>Hi!</b>'

        :type cc: list
        :param cc: CarbonCopy. Example:['a@gmail.com', 'b@gmail.com']

        :type bcc: list
        :param bcc: BlindCarbonCopy. Example:['a@gmail.com', 'b@gmail.com']

        :type attachments: list
        :param attachments: Example:['C:/Users/Administrator/Downloads/apache-maven-3.3.3-bin.zip']

        :rtype boolean
        :return True if send emails successfully. False if fails to send.
        """
        if not self.available:
            log.error(self.error_message)
            return False

        e = email(sender=sender,
                  receivers=receivers,
                  cc=cc,
                  bcc=bcc,
                  subject=subject,
                  content=content,
                  attachments=attachments)

        try:
            response = self.postman.send(e)
            if response.status_code == EMAIL_SMTP_STATUSCODE.SUCCESS:
                return True
            log.error("Send emails fail: " + response.message)
            return False
        except Exception as e:
            log.error(e)
            return False


class VoiceVerify(object):
    """Base and abstract class for voice verify"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def send_voice_verify(self, receiver, content):
        """ Send voice_verify through the service provider

        Example:
            XXX.send_voice_verify("18217511111", "1849")

        :type receiver: str|unicode
        :param receiver: the telephone number. Example:"18217511111"

        :type content: str|unicode
        :param content: the content of voice-verify. Example:"1849"

        :rtype boolean
        :return True if voice verify sends successfully. False if fails to send.
        """
        pass


class DisabledVoiceVerify(VoiceVerify):
    """Do nothing but return False since it's used when the feature is disabled"""

    def send_voice_verify(self, receiver, content):
        log.debug("voice verify is disabled.")
        return False


class RonglianVoiceVerify(VoiceVerify):
    available = False

    account_sid = safe_get_config("voice_verify.rong_lian.account_sid", "")
    auth_token = safe_get_config("voice_verify.rong_lian.auth_token", "")
    app_id = safe_get_config("voice_verify.rong_lian.app_id", "")
    server_ip = safe_get_config("voice_verify.rong_lian.server_ip", "")
    server_port = safe_get_config("voice_verify.rong_lian.server_port", "")
    soft_version = safe_get_config("voice_verify.rong_lian.soft_version", "")
    # optional parameters
    play_times = safe_get_config("voice_verify.rong_lian.play_times", 3)
    display_number = safe_get_config("voice_verify.rong_lian.display_number", "")
    response_url = safe_get_config("voice_verify.rong_lian.response_url", "")
    language = safe_get_config("voice_verify.rong_lian.response_url", "zh")
    # error message if initialization fails
    error_message = ""

    def __init__(self):
        """check voice-verify service parameters from config.py"""
        if self.account_sid == "":
            self.error_message = "VoiceVerify(RongLian) Error: account_sid is empty"
        elif self.auth_token == "":
            self.error_message = "VoiceVerify(RongLian) Error: auth_token is empty"
        elif self.app_id == "":
            self.error_message = "VoiceVerify(RongLian) Error: app_id is empty"
        elif self.server_ip == "":
            self.error_message = "VoiceVerify(RongLian) Error: server_ip is empty"
        elif self.server_port == "":
            self.error_message = "VoiceVerify(RongLian) Error: server_port is empty"
        elif self.soft_version == "":
            self.error_message = "VoiceVerify(RongLian) Error: soft_version is empty"
        else:
            self.available = True

    def send_voice_verify(self, receiver, content):
        """ Send voice_verify through RongLian_YunTongXun service

        Example:
            XXX.send_voice_verify_by_RongLian("18217511111", "1849")

        :type receiver: str|unicode
        :param receiver: the telephone number. Example:"18217511111"

        :type content: str|unicode
        :param content: the content of voice-verify. It should contain 4 words or numbers. Example:"1849"

        :rtype boolean
        :return True if voice-verify sends successfully. False if fails to send.
        """

        if not self.available:
            log.error(self.error_message)
            return False

        # generate voice_verify request
        req = self.__generate_voice_verify_request()

        try:
            # generate request-body
            body = {"to": receiver, "verifyCode": content, "playTimes": self.play_times,
                    "displayNum": self.display_number, "respUrl": self.response_url,
                    "lang": self.language, "appId": self.app_id}
            req.add_data(str(body))

            res = urllib2.urlopen(req)
            data = res.read()
            res.close()
            response = json.loads(data)
            if response["statusCode"] == VOICEVERIFY_RONGLIAN_STATUSCODE.SUCCESS:
                return True
            log.error("Send VoiceVerify(RongLian) fails: " + str(response))
            return False
        except Exception as e:
            log.error(e)
            return False

    def __generate_voice_verify_request(self):
        """ private function to generate voice-verify request through RongLian_YunTongXun_Service

        :rtype object(request)
        :return the object of voice_verify request
        """
        nowdate = datetime.now().strftime("%Y%m%d%H%M%S")
        # generate signature
        signature = self.account_sid + self.auth_token + nowdate
        # hash signature
        sig = hashlib.md5(signature).hexdigest().upper()
        url = "https://%s:%s/%s/Accounts/%s/Calls/VoiceVerify?sig=%s" % (self.server_ip, self.server_port,
                                                                         self.soft_version, self.account_sid, sig)
        # auth
        auth = base64.encodestring(self.account_sid + ":" + nowdate).strip()

        # generate request
        req = urllib2.Request(url)
        req.add_header("Accept", "application/json")
        req.add_header("Content-Type", "application/json;charset=utf-8")
        req.add_header("Authorization", auth)

        return req


class Sms(object):
    """Base and abstract class for SMS"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def send_sms(self, receiver, template_id, content):
        """ Send sms through the service provider

        Example:
            XXX.send_sms("18217511111", SMS_CHINATELECOM_TEMPLATE.DEFAULT, {"param1": "1849"})

        :type receiver: str|unicode
        :param receiver: the telephone number. Example: "18217511111"

        :type template_id: constant integer
        :param template_id: the id of sms-template. Example: SMS_CHINATELECOM_TEMPLATE.DEFAULT

        :type content: dict
        :param content: the content of SMS to replace the slots in sms-template. Example: {"param1":"1849"}

        :rtype boolean
        :return True if SMS sends successfully. False if fails to send.
        """
        pass


class DisabledSms(Sms):
    """Do nothing but return False since it's used when the feature is disabled"""

    def send_sms(self, receiver, template_id, content):
        log.debug("SMS service is disabled.")
        return False


class ChinaTelecomSms(Sms):
    """ Provider SMS service through China Telecom"""
    available = False

    url = safe_get_config("sms.china_telecom.url", "")
    app_id = safe_get_config("sms.china_telecom.app_id", "")
    app_secret = safe_get_config("sms.china_telecom.app_secret", "")
    # url to request access_token
    url_access_token = safe_get_config("sms.china_telecom.url_access_token", "")
    # access_token's expiration time is 30 days.
    access_token = ""
    access_token_expiration_time = None
    # error message if initialization fails
    error_message = ""

    def __init__(self):
        if self.app_id == "":
            self.error_message = "ChinaTelecom-SMS Error: app_id is empty"
        elif self.app_secret == "":
            self.error_message = "ChinaTelecom-SMS Error: app_secret is empty"
        else:
            self.available = True
            self.__get_access_token()

    def send_sms(self, receiver, template_id, content):
        """ Send SMS through ChinaTelecom Plateform

        :type receiver: str|unicode
        :param receiver: the telephone number. Example: "18217511111"

        :type template_id: constant integer
        :param template_id: the id of sms-template. Example: SMS_CHINATELECOM_TEMPLATE.DEFAULT

        :type content: dict
        :param content: the content of SMS to replace slots in sms-template. Example: {"param1":"1849"}

        :rtype boolean
        :return True if SMS sends successfully. False if fails to send.
        """
        if not self.available:
            log.error(self.error_message)
            return False
        elif not self.access_token_expiration_time or self.access_token_expiration_time < get_now():
            if not self.__get_access_token():
                return False

        try:
            # timestamp should be Beijing local time
            timestamp = (get_now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            data = {"acceptor_tel": receiver,
                    "template_id": template_id,
                    "template_param": str(content),
                    "app_id": self.app_id,
                    "access_token": self.access_token,
                    "timestamp": timestamp}
            req = urllib2.Request(self.url)
            post_data = urllib.urlencode(data)
            req.add_data(post_data)
            response = urllib2.urlopen(req)
            response_json = json.loads(response.read())
            if response_json["res_code"] == SMS_CHINATELECOM_STATUSCODE.SUCCESS:
                return True
            log.error("Send SMS(ChinaTelecom) fails: " + str(response_json))
            return False
        except Exception as e:
            log.error(e)
            return False

    def __get_access_token(self):
        """ Request access_token from ChinaTelecom

        :rtype boolean
        :return True if get access_token successfully. False if fails to get.
        """
        data = {"grant_type": "client_credentials",
                "app_id": self.app_id,
                "app_secret": self.app_secret}

        try:
            req = urllib2.Request(self.url_access_token)
            post_data = urllib.urlencode(data)
            req.add_data(post_data)
            response = urllib2.urlopen(req)
            response_json = json.loads(response.read())
            if response_json["res_code"] == CHINATELECOM_ACCESS_TOKEN_STATUSCODE.SUCCESS:
                # access_token's expiration time is 30 days.
                self.access_token = response_json["access_token"]
                self.access_token_expiration_time = get_now() + timedelta(days=30)
                return True
            log.error("ChinaTelecom-SMS Error: request access_token fails")
            return False
        except Exception as e:
            log.error(e)
            return False
