
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
        t = self.db.find_first_object(AdminToken, AdminToken.token==token)
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


    def get_hackid_from_adminid(self, admin_id):

        # can not use backref in db models

        # get emails from admin though admin.id in table admin_email
        admin_emails = self.db.find_all_objects(AdminEmail, AdminEmail.admin_id == admin_id)
        emails = map(lambda x: x.email, admin_emails)

        # get AdminUserHackathonRels from query withn filter by email
        admin_user_hackathon_rels = self.db.find_all_objects(AdminUserHackathonRel, AdminUserHackathonRel.admin_email.in_(emails))

        #get hackathon_ids_from AdminUserHackathonRels details
        hackathon_ids = map(lambda x: x.hackathon_id, admin_user_hackathon_rels)


        return hackathon_ids


    # check the admin authority on hackathon
    def validate_admin_hackathon_request(self, hackathon_id):

        if HTTP_HEADER.TOKEN not in request.headers:
            return True

        hack_ids = self.get_hackid_from_adminid(g.admin.id)

        # get hackathon_id from group and check if its SuperAdmin
        if (-1).in_(hack_ids):
            return True
        else:
            #check  if the hackathon owned by the admin
            return hackathon_id.in_(hack_ids)



admin_manager = AdminManager(db_adapter)

