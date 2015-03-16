import json, os, requests
from config import Config
from flask import session


def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
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


# ---------------common four methods to send http request to remote---------------#
def get_remote(url, headers=None):
    try:
        default_headers = {"content-type": "application/json"}
        if headers is not None and isinstance(headers, dict):
            default_headers.update(headers)
        req = requests.get(url, headers=default_headers)

        if req.status_code >= 200 and req.status_code <= 300:
            resp = json.loads(req.content)
            return convert(resp)
        else:
            return None

    except Exception:
        return None


def post_to_remote(url, post_data, headers=None):
    try:
        default_headers = {"content-type": "application/json"}
        if headers is not None and isinstance(headers, dict):
            default_headers.update(headers)

        req = requests.post(url, data=json.dumps(post_data), headers=default_headers)

        if req.status_code >= 200 and req.status_code <= 300:
            resp = json.loads(req.content)
            return convert(resp)
        else:
            return None

    except Exception:
        return None


def put_to_remote(url, put_data, headers=None):
    try:
        default_headers = {"content-type": "application/json"}
        if headers is not None and isinstance(headers, dict):
            default_headers.update(headers)
        req = requests.put(url, data=json.dumps(put_data), headers=default_headers)

        if req.status_code >= 200 and req.status_code <= 300:
            resp = json.loads(req.content)
            return convert(resp)
        else:
            return None

    except Exception:
        return None


def delete_remote(url, headers=None):
    try:
        default_headers = {"content-type": "application/json"}
        if headers is not None and isinstance(headers, dict):
            default_headers.update(headers)
        req = requests.delete(url, headers=default_headers)

        if req.status_code >= 200 and req.status_code <= 300:
            resp = json.loads(req.content)
            return convert(resp)
        else:
            return None

    except Exception:
        return None

#---------------common four methods to send http request to remote---------------#


#-----------------------Four methods to call backaend API--------------------------#

API_ENDPOINT = safe_get_config('hackathon-api.endpoint', 'http://localhost:15000')


def post_to_apiserver(path, post_data):
    default_headers = {"content-type": "application/json", "token": session['token']}
    return post_to_remote(API_ENDPOINT + path, post_data, headers=default_headers)


def put_to_apiserver(path, post_data):
    default_headers = {"content-type": "application/json", "token": session['token']}
    return put_to_remote(API_ENDPOINT + path, post_data, headers=default_headers)


# It is not necessary to check authority when send GET request
def get_from_apiserver(path):
    return get_remote(API_ENDPOINT + path)


def delete_from_apiserver(path):
    default_headers = {"content-type": "application/json", "token": session['token']}
    return delete_remote(API_ENDPOINT + path, headers=default_headers)

#-----------------------Four methods to call backaend API--------------------------#

