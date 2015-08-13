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

from hackathon import RequiredFeature
from hackathon_response import unauthorized, bad_request, forbidden

__all__ = [
    "token_required",
    "hackathon_name_required",
    "admin_privilege_required",
]

user_manager = RequiredFeature("user_manager")
admin_manager = RequiredFeature("admin_manager")
hack_manager = RequiredFeature("hackathon_manager")


def token_required(func):
    """User must login when this decorator is enabled (for both user and admin)"""

    def authenticate_and_call(*args, **kwargs):
        if not user_manager.validate_login():
            return unauthorized("login required")
        return func(*args, **kwargs)

    # keep the original func name for API intput/output validation where original name is required
    authenticate_and_call.original = func.__name__
    if hasattr(func, "original"):
        authenticate_and_call.original = func.original

    return authenticate_and_call


def hackathon_name_required(func):
    """hackathon_name must be included in header when this decorator is enabled"""

    def authenticate_and_call(*args, **kwargs):
        if not hack_manager.validate_hackathon_name():
            return bad_request("hackathon name invalid")
        return func(*args, **kwargs)

    # keep the original func name for API intput/output validation where original name is required
    authenticate_and_call.original = func.__name__
    if hasattr(func, "original"):
        authenticate_and_call.original = func.original

    return authenticate_and_call


def admin_privilege_required(func):
    """user must login , hackathon_name must be available, and 'user' has proper admin privilege on this hackathon"""

    def authenticate_and_call(*args, **kwargs):
        if not user_manager.validate_login():
            return unauthorized("login required")

        if not hack_manager.validate_hackathon_name():
            return bad_request("hackathon name invalid")

        if not admin_manager.validate_admin_privilege_http():
            return forbidden("access denied")
        return func(*args, **kwargs)

    # keep the original func name for API intput/output validation where original name is required
    authenticate_and_call.original = func.__name__
    if hasattr(func, "original"):
        authenticate_and_call.original = func.original

    return authenticate_and_call
