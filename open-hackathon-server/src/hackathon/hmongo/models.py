# -*- coding: utf-8 -*-
"""
Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
 
The MIT License (MIT)
 
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import sys

sys.path.append("..")
from mongoengine import *
from bson import ObjectId
from datetime import datetime
from uuid import UUID

from hackathon.util import get_now


def make_serializable(item):
    if isinstance(item, list):
        return [make_serializable(sub) for sub in item]
    elif isinstance(item, dict):
        for k, v in item.items():
            item[k] = make_serializable(v)
        return item
    elif isinstance(item, datetime):
        epoch = datetime.utcfromtimestamp(0)
        return long((item - epoch).total_seconds() * 1000)
    elif isinstance(item, ObjectId) or isinstance(item, UUID):
        return str(item)
    else:
        return item


class HDocumentBase(Document):
    """
    DB model base class, providing basic functions
    """

    create_time = DateTimeField(default=get_now())
    update_time = DateTimeField(default=get_now())

    meta = {
        'allow_inheritance': True,
        'abstract': True
    }

    def __init__(self, **kwargs):
        super(HDocumentBase, self).__init__(**kwargs)

    def dic(self):
        return make_serializable(self.to_mongo().to_dict())

    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__, self.to_json())


# Example
#
# class Email(EmbeddedDocument):
#     email = EmailField()
#     test_date = DateTimeField(default=get_now())
#
#
# class Post(HDocumentBase):
#     name = StringField()
#     content = StringField()
#
#     def __init__(self, **kwargs):
#         super(Post, self).__init__(**kwargs)
#
#
# class User(HDocumentBase):
#     password = StringField(max_length=100)
#     name = StringField(max_length=50, min_length=1, required=True)
#     nickname = StringField(max_length=50, min_length=1, required=True)
#     provider = StringField(max_length=20)
#     openid = StringField(max_length=100)
#     avatar_url = StringField(max_length=200)
#     access_token = StringField(max_length=100)
#     online = BooleanField()
#     last_login_time = DateTimeField(default=get_now())
#     login_times = IntField(min_value=0)
#
#     dictf = DictField()
#     emailf = EmailField()
#     embedf = ListField(EmbeddedDocumentField(Email))
#     referf = ReferenceField(Post)
#     urlf = URLField()
#     uuidf = UUIDField()
#
#     def __init__(self, **kwargs):
#         super(User, self).__init__(**kwargs)

class User(HDocumentBase):
    # todo not all fields defined
    name = StringField(max_length=50, min_length=1, required=True)
    nickname = StringField(max_length=50, min_length=1, required=True)
    password = StringField(max_length=100)
    provider = StringField(max_length=20)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)


class UserToken(HDocumentBase):
    token = UUIDField(required=True)
    user_id = ReferenceField(User)
    issue_date = DateTimeField(default=get_now())
    expire_date = DateTimeField(required=True)

    def __init__(self, **kwargs):
        super(UserToken, self).__init__(**kwargs)
