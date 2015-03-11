__author__ = 'root'
import sys

sys.path.append("..")
from hackathon.database.models import Experiment
from sqlalchemy import and_


def get_user_experiment(uid):
    return map(lambda u: u.json(),
               Experiment.query.__filter(and_(Experiment.user_id == uid, Experiment.status < 5)).all())


def get_user_hackathon(uid):
    hackathon = map(lambda u: u.hackathon.json(),
                    Experiment.query.__filter(and_(Experiment.user_id == uid, Experiment.status < 5)).all())
    return [h for h in set(hackathon)]
