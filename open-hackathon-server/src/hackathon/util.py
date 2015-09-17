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
from datetime import datetime

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
