from database import *
from log import log
from datetime import datetime


class Registration:

    def get_by_email(self, email):
        return Register.query.filter_by(email=email, enabled=1).first()


    def get_all(self):
        return Register.query.filter_by(enabled=1).all()

    def submit(self, args):
        if "id" not in args:
            log.warn("cannot submit expr for the lack of id")
            raise Exception("id unavailable")

        id = args["id"]
        u = Register.query.filter_by(id=id).first()
        if u is None:
            log.debug("register user not found:" + id)
            return "user not found", 404

        u.online = args["online"] if "online" in args else u.online
        u.submitted = args["submitted"] if "submitted" in args else u.submitted
        u.submitted_time = datetime.utcnow()
        db.session.commit()
        return u
