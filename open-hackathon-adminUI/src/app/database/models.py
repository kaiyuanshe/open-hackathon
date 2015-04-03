# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#  
# The MIT License (MIT)
#  
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#  
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#  
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------

import sys

sys.path.append("..")
from . import db
from datetime import datetime
import json
from sqlalchemy import DateTime


def date_serializer(date):
    return long((date - datetime(1970, 1, 1)).total_seconds() * 1000)


def to_dic(inst, cls):
    # add your coversions for things like datetime's
    # and what-not that aren't serializable.
    convert = dict()
    convert[DateTime] = date_serializer

    d = dict()
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        if c.type.__class__ in convert.keys() and v is not None:
            try:
                func = convert[c.type.__class__]
                d[c.name] = func(v)
            except:
                d[c.name] = "Error:  Failed to covert using ", str(convert[c.type.__class__])
        # elif v is None:
        # d[c.name] = str()
        else:
            d[c.name] = v
    return d


def to_json(inst, cls):
    return json.dumps(to_dic(inst, cls))


class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    nickname = db.Column(db.String(50))
    openid = db.Column(db.String(100))
    avatar_url = db.Column(db.String(200))
    access_token = db.Column(db.String(100))
    online = db.Column(db.Integer)  # 0:offline 1:online
    create_time = db.Column(db.DateTime)
    last_login_time = db.Column(db.DateTime)

    def get_admin_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.get_admin_id())

    def dic(self):
        return to_dic(self, self.__class__)

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(AdminUser, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()
        if self.last_login_time is None:
            self.last_login_time = datetime.utcnow()

    def __repr__(self):
        return "AdminUser: " + self.json()


class AdminEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120))
    primary_email = db.Column(db.Integer)  # 0:NOT Primary Email 1:Primary Email
    verified = db.Column(db.Integer)  # 0 for not verified, 1 for verified

    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id', ondelete='CASCADE'))
    admin = db.relationship('AdminUser', backref=db.backref('emails', lazy='dynamic'))

    def dic(self):
        return to_dic(self, self.__class__)

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(AdminEmail, self).__init__(**kwargs)


class AdminToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(50), unique=True, nullable=False)

    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id', ondelete='CASCADE'))
    admin = db.relationship('AdminUser', backref=db.backref('tokens', lazy='dynamic'))

    issue_date = db.Column(db.DateTime)
    expire_date = db.Column(db.DateTime, nullable=False)

    def dic(self):
        return to_dic(self, self.__class__)

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(AdminToken, self).__init__(**kwargs)
        if self.issue_date is None:
            self.issue_date = datetime.utcnow()

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

    def dic(self):
        return to_dic(self, self.__class__)

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(AdminUserHackathonRel, self).__init__(**kwargs)

    def __repr__(self):
        return "AdminUserHackathonRel: " + self.json()
