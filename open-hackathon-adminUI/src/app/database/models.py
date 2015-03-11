import sys
import email

sys.path.append("..")
from . import UserMixin
from . import db
from datetime import datetime
import json


def to_json(inst, cls):
    # add your coversions for things like datetime's
    # and what-not that aren't serializable.
    convert = dict()
    convert[db.DateTime] = str

    d = dict()
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        if c.type.__class__ in convert.keys() and v is not None:
            try:
                func = convert[c.type.__class__]
                d[c.name] = func(v)
            except:
                d[c.name] = "Error:  Failed to covert using ", str(convert[c.type.__class__])
        elif v is None:
            d[c.name] = str()
        else:
            d[c.name] = v
    return json.dumps(d)



class AdminUser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    nickname = db.Column(db.String(50))
    openid = db.Column(db.String(100))
    avatar_url = db.Column(db.String(200))
    access_token = db.Column(db.String(100))
    online = db.Column(db.Integer)  # 0:offline 1:online
    create_time = db.Column(db.DateTime)
    last_login_time = db.Column(db.DateTime)

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(AdminUser, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()
        if self.last_login_time is None:
            self.last_login_time = datetime.utcnow()
#        if self.slug is None:
#            self.slug = str(uuid.uuid1())[0:8]  # todo generate a real slug


class AdminEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120))
    primary_email = db.Column(db.Integer)  # 0:NOT Primary Email 1:Primary Email
    verified = db.Column(db.Integer)  # 0 for not verified, 1 for verified

    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id', ondelete='CASCADE'))
    admin = db.relationship('AdminUser', backref=db.backref('emails', lazy='dynamic'))

    def __init__(self, **kwargs):
        super(AdminEmail, self).__init__(**kwargs)



class AdminToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(50), unique=True, nullable=False)

    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id', ondelete='CASCADE'))
    admin = db.relationship('AdminUser', backref=db.backref('tokens', lazy='dynamic'))

    issue_date = db.Column(db.DateTime)
    expire_date = db.Column(db.DateTime, nullable=False)

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(AdminToken, self).__init__(**kwargs)
        if self.issue_date is None:
            issue_date = datetime.utcnow()

    def __repr__(self):
        return "AdminToken: " + self.json()


class AdminUserHackathonRel(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    admin_email = db.Column(db.String(120))
    role_type = db.Column(db.Integer)
    hackathon_id = db.Column(db.Integer)
    state = db.Column(db.Integer)
    remarks = db.Column(db.String(255))
    create_time = db.Column(db.DateTime)


    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(AdminUserHackathonRel, self).__init__(**kwargs)

    def __repr__(self):
        return "AdminUserGroup: " + self.json()