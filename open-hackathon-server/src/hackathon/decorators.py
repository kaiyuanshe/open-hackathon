# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

from hackathon import RequiredFeature
from hackathon.hackathon_response import unauthorized, bad_request, forbidden

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
        if not user_manager.validate_token():
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
        if not user_manager.validate_token():
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
