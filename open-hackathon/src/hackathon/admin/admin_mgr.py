# import sys
#
# sys.path.append("..")
# from hackathon.database.models import AdminToken
# from hackathon.database import db_adapter
# from datetime import datetime
# from hackathon.constants import HTTP_HEADER
#
# from flask import request, g
#
#
#
# class AdminManager(object):
#     def __init__(self, db_adapter):
#         self.db = db_adapter
#
#     def __validate_token(self, token):
#         t = self.db.find_first_object(AdminToken, token=token)
#         if t is not None and t.expire_date >= datetime.utcnow():
#             return t.admin
#         return None
#
#
#     def validate_request(self):
#         if HTTP_HEADER.TOKEN not in request.headers:
#             return False
#
#         admin = self.__validate_token(request.headers[HTTP_HEADER.TOKEN])
#         if admin is None:
#             return False
#
#         g.admin = admin
#         return True
#
#
# admin_manager = AdminManager(db_adapter)