import urllib, urllib2, httplib, json, os, requests
from datetime import datetime

from config import Config

# common functions


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
    for arg in key.split("/"):
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


# move to common.py for re-use
def post_to_remote(url, post_data, headers={"content-type": "application/json"}):
    req = requests.post(url, data=json.dumps(post_data), headers=headers)
    resp = json.loads(req.content)

    return convert(resp)

    # end


def get_remote(url, accept=None):
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url)
    if accept is not None:
        request.add_header("Accept", accept)
    resp = opener.open(request)
    return resp.read()


def delete_remote(url):
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url)
    request.get_method = lambda: 'DELETE'
    resp = opener.open(request)
    return "OK"


def get_class(kls):
    # kls is the full name of a class obj. e.g. "hackathon.registration.Registration"
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m