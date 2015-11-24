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

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from functions import safe_get_config

# flask
app = Flask(__name__)

app.config['SECRET_KEY'] = safe_get_config("app.secret_key", "secret_key")

app.config['DEBUG_TB_ENABLED'] = False
toolbar = DebugToolbarExtension(app)


class Context(object):
    """Helper class for JSON. We can access dict similarly as literal in JS

    Essentially a collection of parameters that will be passed through threads/databases
    NEVER put complex object in Context such as instance of db models or business manager

    ::Example:
        dic = {"a": "va", "b": {"b1": "b1", "b2": [1, 2, 3], "b3": [{"b3a": "b3a"}]}}
        c = Context.from_object(dic) # convert existing obj to Context

        print c.a
        print c["a"] # exactly the same as c.a. But it allows you pass values to key

        key = "test"
        print c[key] # now c[key] == c["test"] but c.key != c["test"], actually c.key=c["key"]

        print c.b.b1
        print c.b.b3[0].b3a

        print c.get("c", 3) # unlike c.a or c["a"], get won't raise exception if key not found
        print c.get("c")

        c.c1 = True # you can set attribute any time
        print c.get("c1")

        ctx = Context("a"="a-v","b"="b-v") # you can also create instance directly through constructor
        ctx.c = "c-v"
        print ctx.a
        print ctx["c"]

    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__dict__[key] = value

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]

        raise AttributeError()

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)

    def __repr__(self):
        return repr(self.__dict__)

    def __contains__(self, key):
        return key in self.__dict__

    def get(self, key, default_value=None):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            return default_value

    @staticmethod
    def from_object(arg):
        """Convert JSON-like object to Context recursively

        :returns list of Context if arg is list
                 instance of Context if arg is dict
                 the original arg otherwise
        """
        if isinstance(arg, list):
            return [Context.from_object(a) for a in arg]
        elif isinstance(arg, dict):
            ctx = Context()
            for k, v in arg.iteritems():
                if isinstance(v, dict):
                    setattr(ctx, k, Context.from_object(v))
                elif isinstance(v, list):
                    setattr(ctx, k, [Context.from_object(vv) for vv in v])
                else:
                    setattr(ctx, k, v)

            return ctx
        else:
            return arg


from views import *
