from flask import g
from functools import wraps


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