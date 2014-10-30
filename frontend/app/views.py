from flask import render_template, flash, redirect,request
from app import app
import httplib
import urllib , urllib2
import json
import uuid
from app import config
from database import init_db
from database import db_session
from models import User
#from forms import LoginForm

def query_info(website,url,ssl):
    if (ssl == 1):
        conn = httplib.HTTPConnection(website);
    else:
        conn = httplib.HTTPSConnection(website);
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

@app.route('/')
@app.route('/index')
def index():
        return render_template("index.html")
@app.route('/PrivacyStatement')
def PrivacyStatement():
    return render_template("PrivacyStatement.html")
@app.route('/TermsOfUse')
def TermsOfUse():
    return render_template("TermsOfUse.html")
@app.route('/paper')
def paper():
    return render_template("paper.html")
@app.route('/paper2')
def paper22():
    return render_template("paper2.html")
@app.route('/test')
def test():
    return render_template("test.html")
@app.route('/google')
def google():
    return render_template("google.html")
@app.route('/github')
def github():
    code = request.args.get('code')
    url = config.GITHUB_URL1 + code
    httpres = query_info('github.com',url,2);
    url_ori = httpres.read()
    start = url_ori.index('=')
    end = url_ori.index('&')
    #Str = request.query_string
    access_token = url_ori[start+1:end]
    url = '/user?access_token=' + access_token
    conn = httplib.HTTPSConnection('api.github.com')
    conn.request('GET',url,'',{'user-agent':'flask'})
    #conn.putheader('User-Agent','flask')
    httpres = conn.getresponse()
    info = json.loads(httpres.read())
    name = 'github' + str(info['id'])
    uid = str(uuid.uuid3(uuid.NAMESPACE_DNS,name))
    query = db_session.query(User)
    result = query.filter(User.uid == uid).first()
    if (result == None):
        u = User(info['login'],uid,'github')
        db_session.add(u)
        db_session.commit()
    #print info
    return render_template("github.html",pic=info['id'],name=info['login'])
    #return render_template("github.html",iden=httpres.read(),name='bbb')
@app.route('/qq')
def qq():
    code = request.args.get('code')
    #print code
    url =  config.QQ_URL + code + '&state=osslab'
    httpres = query_info('graph.qq.com',url,2)
    url_ori = httpres.read()
    start = url_ori.index('=')
    end = url_ori.index('&')
    access_token = url_ori[start+1:end]
    url = '/oauth2.0/me?access_token=' + access_token
    httpres = query_info('graph.qq.com',url,2)
    info = httpres.read()
    info = info[10:-4]
    info = json.loads(info)
    openid=info['openid']
    appid = info['client_id']
    url = '/user/get_user_info?access_token=' + access_token + '&oauth_consumer_key=' +appid +'&openid=' + openid
    httpres = query_info('graph.qq.com',url,2)
    info = json.loads(httpres.read())   
    return render_template("qq.html",name=info['nickname'],pic=info['figureurl'])
@app.route('/renren')
def renren():
    url_ori = request.url
    #if (url.ori.find('access_token') < 0) return render_template("renren.html",iden=url_ori,name='bb')
    if (len(url_ori)<50):
        return render_template("renren.html",iden=url_ori,name='bb')
    start = url_ori.index('=')
    end = url_ori.index('&')
    #Str = request.query_string
    access_token = url_ori[start+1:end]
    url = '/v2/user/get?access_token=' + access_token
    httpres = query_info('api.renren.com',url,2)
    #info = httpres.read()
    info = json.loads(httpres.read())
    name = 'renren' + str(info['response']['id'])
    uid = str(uuid.uuid3(uuid.NAMESPACE_DNS,name))
    query = db_session.query(User)
    result = query.filter(User.uid == uid).first()
    #result = session.query(User).filter(User.uid == uid).all()
    if (result == None):
        u = User(info['response']['name'],uid,'renren')
        db_session.add(u)
        db_session.commit()
    #info = Str
    #return render_template("renren.html")
    #return render_template("renren.html",iden=url_ori,name='cc')
    return render_template("renren.html",pic = info['response']['avatar'][0]['url'],name=info['response']['name'])
@app.route('/course')
def course():
    typecode = request.args.get('type')
    username = request.cookies.get('username')
    url = request.cookies.get('picurl')
    data = mapper(int(typecode),username)
    #data = {'request':'1', 'client_id':username, 'image':'python','protocol':'ssh'}
    url2 = config. APISERVER
    data = urllib.urlencode(data)
    req = urllib2.Request(url = url2 , data = data)
    res_data = urllib2.urlopen(req)
    res = 'http://' + res_data.read()
    return render_template("course.html",name=username,pic=url,vm = res)
@app.route('/test_ice')
def test_ice():
    return render_template("test_ice.html")

