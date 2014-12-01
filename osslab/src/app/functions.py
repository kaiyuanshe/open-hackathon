import urllib, urllib2, httplib, json

from config import Config

# common functions


def convert(input):
    if isinstance(input, dict):
        return {convert(key):convert(value) for key,value in input.iteritems()}
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
    r= get_config(key)
    return r if r is not None else default_value

# move to common.py for re-use
def post_to_remote(url, post_data, contentType='application/json'):
    req = urllib2.Request(url)
    req.add_header('Content-Type', contentType)
    f = urllib2.urlopen(req, json.dumps(post_data))
    resp = f.read()
    f.close()
    return convert(json.loads(resp))

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
    request.get_method = lambda : 'DELETE'
    resp = opener.open(request)
    return "OK"
