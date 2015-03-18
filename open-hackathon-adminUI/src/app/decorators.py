
from functools import wraps
from flask import g
from admin.admin_mgr import admin_manager

def role_required(role):
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if role is None:
                return func(*args, **kwargs)
            else:
                return g.admin.is_authenticated() and admin_manager.check_role(role) and func(*args, **kwargs)

        return decorated_view

    return wrapper