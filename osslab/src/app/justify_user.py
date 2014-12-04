from database import *


class justifyUser:

    def justify(self, email):
        q = Register.query.filter(Register.email == email).all()
        if len(q) == 0:
            return False
        else:
            return True


