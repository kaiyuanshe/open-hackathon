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

from flask import g
from functools import wraps
from user import user_manager
from admin.admin_mgr import admin_manager


def role_required(*roles):
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if len(roles) == 0:
                return func(*args, **kwargs)
            else:
                return g.user.is_authenticated() and g.user.has_roles(*roles) and func(*args, **kwargs)

        return decorated_view

    return wrapper


def token_required(func):
    def authenticate_and_call(*args, **kwargs):
        if not user_manager.validate_request():
            return "Access Denied", 403
        return func(*args, **kwargs)

    return authenticate_and_call


def admin_token_required(func):
    def authenticate_and_call(*args, **kwargs):
        if not admin_manager.validate_request():
            return "Access Denied", 403
        return func(*args, **kwargs)

    return authenticate_and_call


def hackathon_id_required(func):
    def authenticate_and_call(*args, **kwargs):
        if not admin_manager.validate_hackathon_id():
            return "Access Denied", 403
        return func(*args, **kwargs)

    return authenticate_and_call