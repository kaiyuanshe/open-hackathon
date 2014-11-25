from app import app
from sqlalchemy.orm import sessionmaker
from database import *

class justifyUser:
    def __init__(self):
        self.engine = db.get_engine(app)

    def justify(self, user_email):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        q = session.query(User).filter(User.email == user_email).all()
        if len(q) == 0:
            return False
        else:
            return True


