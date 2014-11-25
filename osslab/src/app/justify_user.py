from database import *


class justifyUser:

    def justify(self, user_email):
        q = User.query().filter(User.email == user_email).all()
        if len(q) == 0:
            return False
        else:
            return True


