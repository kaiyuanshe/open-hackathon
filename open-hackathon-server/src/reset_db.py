# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

from hackathon.hmongo import drop_db
from setup_db import setup_db

drop_db()
setup_db()
