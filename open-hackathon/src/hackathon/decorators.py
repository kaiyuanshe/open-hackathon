
from admin.admin_mgr import admin_manager


def admin_token_required(func):

    def authenticate_and_call(*args, **kwargs):
        #Tdefine check administarton's token function
        if not admin_manager.validate_request():
            return "Access Denied", 403
        return func(*args, **kwargs)

    return authenticate_and_call
