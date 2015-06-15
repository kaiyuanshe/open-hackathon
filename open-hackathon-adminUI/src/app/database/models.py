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
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, TypeDecorator
from sqlalchemy.orm import backref, relation
from . import Base, db_adapter
from datetime import datetime
from app.functions import get_now
import json
from pytz import utc
from dateutil import parser


def relationship(*arg, **kw):
    ret = relation(*arg, **kw)
    db_adapter.commit()
    return ret


def date_serializer(date):
    return long((date - datetime(1970, 1, 1)).total_seconds() * 1000)


def to_dic(inst, cls):
    # add your coversions for things like datetime's
    # and what-not that aren't serializable.
    convert = dict()
    convert[DateTime] = date_serializer
    convert[TZDateTime] = date_serializer

    d = dict()
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        if c.type.__class__ in convert.keys() and v is not None:
            try:
                func = convert[c.type.__class__]
                d[c.name] = func(v)
            except:
                d[c.name] = "Error:  Failed to covert using ", str(convert[c.type.__class__])
        else:
            d[c.name] = v
    return d


def to_json(inst, cls):
    return json.dumps(to_dic(inst, cls))


class TZDateTime(TypeDecorator):
    """
    Coerces a tz-aware datetime object into a naive utc datetime object to be
    stored in the database. If already naive, will keep it.
    On return of the data will restore it as an aware object by assuming it
    is UTC.
    Use this instead of the standard :class:`sqlalchemy.types.DateTime`.
    """
    impl = DateTime

    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, basestring) or isinstance(value, str):
                value = parser.parse(value)
            if isinstance(value, datetime):
                if value.tzinfo is not None:
                    value = value.astimezone(utc)
                    value.replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if isinstance(value, datetime):
                if value.tzinfo is not None:
                    value = value.astimezone(utc)
                    value.replace(tzinfo=None)
        return value


class DBBase(Base):
    """
    DB model base class, providing basic functions
    """
    __abstract__ = True

    def __init__(self, **kwargs):
        super(DBBase, self).__init__(**kwargs)

    def dic(self):
        return to_dic(self, self.__class__)

    def json(self):
        return to_json(self, self.__class__)

    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__, self.json())


class User(DBBase):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    password = Column(String(100))  # encrypted password for the default admin/guest users.
    name = Column(String(50))
    nickname = Column(String(50))
    provider = Column(String(20))
    openid = Column(String(100))
    provider = Column(String(20))
    avatar_url = Column(String(200))
    access_token = Column(String(100))
    online = Column(Integer)  # 0:offline 1:online
    create_time = Column(TZDateTime, default=get_now())
    last_login_time = Column(TZDateTime, default=get_now())

    def get_user_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.get_user_id())

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)


class UserEmail(DBBase):
    __tablename__ = 'user_email'

    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    email = Column(String(120))
    primary_email = Column(Integer)  # 0:NOT Primary Email 1:Primary Email
    verified = Column(Integer)  # 0 for not verified, 1 for verified
    create_time = Column(TZDateTime, default=get_now())
    update_time = Column(TZDateTime)

    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('User', backref=backref('emails', lazy='dynamic'))

    def get_user_email(self):
        return self.email


class UserToken(DBBase):
    __tablename__ = 'user_token'

    id = Column(Integer, primary_key=True)
    token = Column(String(50), unique=True, nullable=False)

    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('User', backref=backref('tokens', lazy='dynamic'))

    issue_date = Column(TZDateTime, default=get_now())
    expire_date = Column(TZDateTime, nullable=False)

    def __init__(self, **kwargs):
        super(UserToken, self).__init__(**kwargs)


class AdminHackathonRel(DBBase):
    __tablename__ = 'admin_hackathon_rel'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('User', backref=backref('admin_hackathon_rels', lazy='dynamic'))

    role_type = Column(Integer)  # enum.ADMIN_ROLE_TYPE
    hackathon_id = Column(Integer)
    status = Column(Integer)
    remarks = Column(String(255))
    create_time = Column(TZDateTime, default=get_now())
    update_time = Column(TZDateTime)

    def __init__(self, **kwargs):
        super(AdminHackathonRel, self).__init__(**kwargs)

