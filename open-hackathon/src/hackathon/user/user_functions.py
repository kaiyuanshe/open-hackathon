__author__ = 'root'
import sys

sys.path.append("..")
from hackathon.database.models import Experiment, Register, User, UserEmail
from hackathon.database import db_adapter
from sqlalchemy import and_


def get_user_experiment(uid):
    return map(lambda u: u.json(),
               Experiment.query.filter(and_(Experiment.user_id == uid, Experiment.status < 5)).all())


def get_user_hackathon(uid):
    hackathon = map(lambda u: u.hackathon.json(),
                    Experiment.query.filter(and_(Experiment.user_id == uid, Experiment.status < 5)).all())
    return [h for h in set(hackathon)]


def get_hackathon_stat(hackathon_id):
    reg_email_list = map(lambda r: r.email, db_adapter.find_all_objects(Register, hackathon_id=hackathon_id, enabled=1))
    reg_count = len(reg_email_list)
    stat = {
        "total": reg_count,
        "hid": hackathon_id,
        "online": 0,
        "offline": reg_count
    }
    if (reg_count > 0):
        user_id_list = map(lambda ue: ue.user_id, UserEmail.query.filter(UserEmail.email.in_(reg_email_list)).all())
        online_count = User.query.filter(User.id.in_(user_id_list)).count()
        stat["online"] = online_count
        stat["offline"] = reg_count - online_count

    return stat