import sys

sys.path.append("..")
from hackathon.database.models import Hackathon, User, UserEmail, Register
from hackathon.database import db_adapter


class HackathonManager():
    def __init__(self, db):
        self.db = db

    def get_hackathon_by_name(self, name):
        return self.db.find_first_object_by(Hackathon, name=name)

    def get_hackathon_by_id(self, hackathon_id):
        return self.db.find_first_object_by(Hackathon, id=hackathon_id)

    def get_hackathon_stat(self, hackathon_id):
        reg_email_list = [r.email for r in self.db.find_all_objects_by(Register, hackathon_id=hackathon_id, enabled=1)]
        reg_count = len(reg_email_list)
        stat = {
            "total": reg_count,
            "hid": hackathon_id,
            "online": 0,
            "offline": reg_count
        }
        if reg_count > 0:
            user_id_list = [x.user_id for x in self.db.find_all_objects(UserEmail, UserEmail.email.in_(reg_email_list))]
            user_id_online = self.db.count(User, (User.id.in_(user_id_list) & (User.online == 1)))
            stat["online"] = user_id_online
            stat["offline"] = reg_count - user_id_online

        return stat

    def get_hackathon_list(self, name=None):
        if name is not None:
            return db_adapter.find_first_object_by(Hackathon, name=name).json()
        return map(lambda u: u.json(), db_adapter.find_all_objects(Hackathon))


hack_manager = HackathonManager(db_adapter)