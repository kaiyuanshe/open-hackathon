__author__ = 'root'

from database.models import Experiment
from sqlalchemy import and_


def get_user_experiment(uid):
    return map(lambda u: u.hackathon.json(),
               Experiment.query.filter(and_(Experiment.user_id == uid, Experiment.status < 5)).all())

def get_user_hackathon(uid):
    hackathon = get_user_experiment(uid)
    return [h for h in set(hackathon)]