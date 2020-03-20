# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import json, os, requests, urllib.request, urllib.error, urllib.parse
from datetime import datetime
from urllib.parse import parse_qs
import ssl
from flask import jsonify

try:
    from config import Config
except ImportError:
    from client.config_sample import Config


def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.items()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, str):
        return input.encode('utf-8')
    else:
        return input


def get_config(key):
    ret = Config
    for arg in key.split("."):
        if arg in ret and isinstance(ret, dict):
            ret = ret[arg]
        else:
            return None
    return ret


def safe_get_config(key, default_value):
    r = get_config(key)
    return r if r is not None else default_value


def mkdir_safe(path):
    if path and not (os.path.exists(path)):
        os.makedirs(path)
    return path


def get_class(kls):
    # kls is the full name of a class obj. e.g. "hackathon.registration.Registration"
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def post_to_remote(url, post_data, headers=None):
    ssl.match_hostname = lambda cert, hostname: True
    default_headers = {"content-type": "application/json"}
    if headers is not None and isinstance(headers, dict):
        default_headers.update(headers)
    req = requests.post(url, data=json.dumps(post_data), headers=default_headers)
    resp = json.loads(req.content)

    return convert(resp)


def put_to_remote(url, post_data, headers=None):
    ssl.match_hostname = lambda cert, hostname: True
    default_headers = {"content-type": "application/json"}
    if headers is not None and isinstance(headers, dict):
        default_headers.update(headers)
    req = requests.put(url, data=json.dumps(post_data), headers=default_headers)
    resp = json.loads(req.content)

    return convert(resp)


def get_remote(url, headers={}):
    # ssl.match_hostname = lambda cert, hostname: True
    # opener = urllib.request.build_opener(urllib.request.HTTPHandler)
    # request = urllib.request.Request(url, None, headers)
    # print(request)
    # resp = opener.open(request)
    # print(resp.read())
    r = requests.get(url, headers=headers)
    # print(r.text)
    # print(jsonify(r.text))
    r.encoding = r.apparent_encoding
    # return resp.read()
    return r.text


def delete_remote(url, headers=None):
    ssl.match_hostname = lambda cert, hostname: True
    default_headers = {"content-type": "application/json"}
    if headers is not None and isinstance(headers, dict):
        default_headers.update(headers)

    opener = urllib.request.build_opener(urllib.request.HTTPHandler)
    request = urllib.request.Request(url, headers=default_headers)
    request.get_method = lambda: 'DELETE'
    opener.open(request)

    return "OK"


def get_now():
    return datetime.utcnow()  # tzinfo=None


def qs_dict(query):
    return dict([(k, v[0]) for k, v in list(parse_qs(query).items())])

def is_local():
    return safe_get_config("environment", "local") == "local"