from sqlalchemy import Column, Integer, String, VARCHAR
from database import Base

class User(Base):
    __tablename__ = 'users'
    uid = Column(VARCHAR(128),primary_key=True)
    name = Column(VARCHAR(128))
    scope = Column(VARCHAR(20))
    email=Column(VARCHAR(128))

    def __init__(self, name = None , uid = None, scope = None,email=None):
        self.name = name
        self.uid = uid
        self.scope = scope
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.name)
