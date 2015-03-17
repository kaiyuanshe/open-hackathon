
from functools import wraps
from flask import g

def role_required(role):
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if role is None:
                return func(*args, **kwargs)
            else:
                return g.admin.is_authenticated() and g.admin.check_role(role) and func(*args, **kwargs)

        return decorated_view

    return wrapper