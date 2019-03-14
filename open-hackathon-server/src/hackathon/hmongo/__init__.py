# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import sys

sys.path.append("..")
from mongoengine import connect

from hackathon.util import safe_get_config

__all__ = ["db",
           "drop_db"]

mongodb_host = safe_get_config("mongodb.host", "localhost")
mongodb_port = safe_get_config("mongodb.port", 27017)
ohp_db = safe_get_config("mongodb.database", "hackathon")

# mongodb client
client = connect(ohp_db, host=mongodb_host, port=mongodb_port)

# mongodb collection for OHP, authentication disabled for now.
db = client[ohp_db]


# db.authenticate('user', 'password', mechanism='SCRAM-SHA-1')


def drop_db():
    client.drop_database(ohp_db)
