import sys

sys.path.append("..")
from hackathon.database.models import *
from hackathon.database import db_adapter
from datetime import datetime
from hackathon.constants import HTTP_HEADER
from flask import request, g



class AdminManager(object):
    def __init__(self, db_adapter):
        self.db = db_adapter

    def __validate_token(self, token):
        t = self.db.find_first_object(AdminToken, token=token)
        if t is not None and t.expire_date >= datetime.utcnow():
            return t.admin
        return None

    def validate_request(self):
        if HTTP_HEADER.TOKEN not in request.headers:
            return False

        admin = self.__validate_token(request.headers[HTTP_HEADER.TOKEN])
        if admin is None:
            return False

        g.admin = admin
        return True



    def get_hackid_from_token(self):

        admin = self.__validate_token(request.headers[HTTP_HEADER.TOKEN])
        # Even thought there would be more than one results ,  just get only one to access from checking email
        email = admin.emails[0]['email']

        # get AdminGroup from AdminUserGroup ,get AdminUserGroup from query filter by email
        group = self.db.find_first_object(AdminUserGroup,email=email).admin_group

        return group.hackathon_id


    #check the admin authority on hackathon
    def validate_hackathon_request(self,hackathon_id):

        if HTTP_HEADER.TOKEN not in request.headers:
            return False

        hack_id = self.get_hackid_from_token()

        # get hackathon_id from group and check if its SuperAdmin
        if hack_id == -1 :
            return True
        # if not check the hackathon owned by the admin, maybe this value is a list
        else:
            if hackathon_id.in_(hack_id):
                return True
            else:
                return False


admin_manager = AdminManager(db_adapter)