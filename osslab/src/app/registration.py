from database import *


class Registration:

    def get_by_email(self, email):
        return Register.query.filter_by(email=email).first()


