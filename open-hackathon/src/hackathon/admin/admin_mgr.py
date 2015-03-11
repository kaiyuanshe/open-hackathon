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


    def get_hackid_from_adminID(self, admin_id):

        # can not use backref in db models

        # get emails from admin though admin.id in table admin_email
        admin_emails = self.db.filter(AdminEmail, AdminEmail.admin_id == admin_id)
        emails = map(lambda x: x.email, admin_emails.all())

        # get AdminUserGroup from query withn filter by email
        admin_user_groups = self.db.filter(AdminUserGroup, AdminUserGroup.admin_email.in_(emails))

        #get AdminGroup though admin_user_group's group_id
        admin_group_ids = map(lambda x: x.group_id, admin_user_groups.all())
        admin_groups = self.db.filter(AdminGroup, AdminGroup.id.in_(admin_group_ids))

        #get hackathon_id from AdminGroup details
        hackathon_ids = admin_group_ids = map(lambda x: x.hackathon_id, admin_groups.all())

        return hackathon_ids


    # check the admin authority on hackathon
    def validate_hackathon_request(self, hackathon_id):

        if HTTP_HEADER.TOKEN not in request.headers:
            return False

        hack_ids = self.get_hackid_from_adminID(g.admin.id)

        # get hackathon_id from group and check if its SuperAdmin
        if hack_ids[0] == -1:
            return True
        # if not check the hackathon owned by the admin, maybe this value is a list
        else:
            if hackathon_id.in_(hack_ids):
                return True
            else:
                return False


admin_manager = AdminManager(db_adapter)