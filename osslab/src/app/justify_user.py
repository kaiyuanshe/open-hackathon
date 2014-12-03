from database import *


class JustifyUser:

    def justify(self, email):
        return Register.query.filter_by(email=email).first()


