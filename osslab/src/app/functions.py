import httplib

from config import Config


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

def query_info(website,url,ssl):
    if (ssl == 1):
        conn = httplib.HTTPConnection(website)
    else:
        conn = httplib.HTTPSConnection(website)
    conn.request('GET',url)
    httpres = conn.getresponse()
    return httpres

def add_head_href(head,href):
    arr = href.split('href="')
    href = ('href="' + head).join(arr)
    arr = href.split('src="')
    href = ('src="' + head).join(arr)
    return href

def mapper(typecode , username):
    ret = {}
    ret['request'] = '1'
    ret['client_id'] = username
    if (typecode == 8):
        ret['protocol'] = 'rdp'
    if (typecode < 8):
        ret['protocol'] = 'ssh'
    if (typecode == 1):
        ret['image'] = 'python'
    elif (typecode == 2):
        ret['image'] = 'ruby'
    elif (typecode == 3):
        ret['image'] = 'nodejs'
    elif (typecode == 4):
        ret['image'] = 'perl'
    elif (typecode == 5):
        ret['image'] = 'mysql'
    elif (typecode == 6):
        ret['image'] = 'mongodb'
    elif (typecode == 7):
        ret['image'] = 'redis'
    elif (typecode == 8):
        ret['image'] = 'typescript'
    return ret