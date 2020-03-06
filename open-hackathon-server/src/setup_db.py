# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

# try:
from .hackathon.hmongo.models import User
# except ImportError:
#     pass


def setup_db():
    """Initialize db tables

    make sure database and user correctly created in db
    in case upgrade the table structure, the origin table need be dropped firstly
    """
    # init REQUIRED db data.

    # reserved user is deleted, may not need in mongodb implementation

    # default super admin

    admin = User(
        name="admin",
        nickname="admin",
        password="e8104164dfc4a479e42a9f6c0aefd2be",
        avatar_url="/static/pic/monkey-32-32px.png",
        is_super=True)

    User.objects(name="admin").update_one(__raw__={"$set": admin.to_mongo().to_dict()}, upsert=True)


setup_db()
