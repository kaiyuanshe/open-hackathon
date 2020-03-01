# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

from constants import HTTP_HEADER
from flask import session
from functions import safe_get_config


def __get_headers(hackathon_id):
    return {
        "content-type": "application/json",
        HTTP_HEADER.TOKEN: session[HTTP_HEADER.TOKEN] if HTTP_HEADER.TOKEN in session else "",
        HTTP_HEADER.HACKATHON_ID: hackathon_id
    }


def __get_uri(path):
    if path.startswith("/"):
        path = path.lstrip("/")
    return "%s/%s" % (safe_get_config('endpoint.hackathon_api', 'http://localhost:15000'), path)
