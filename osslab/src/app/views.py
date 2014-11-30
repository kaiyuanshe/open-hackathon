import uuid
from flask import request, Response
from flask.ext.restful import Api, Resource
from app import app
from functions import *
from routes import *


api = Api(app)

# index page
@app.route('/')
@app.route('/index')
def index():
    return simple_route("index")

# error handler for 404
@app.errorhandler(404)
def page_not_found(error):
    # render a beautiful 404 page
    return "Page not Found", 404

# error handler for 500
@app.errorhandler(500)
def internal_error(error):
    # render a beautiful 500 page
    return "Internal Server Error", 500

# simple webPages
@app.route('/<path:path>')
def template_routes(path):
    return simple_route(path)

# js config
@app.route('/config.js')
def js_config():
    resp =  Response(response="var CONFIG=%s" % json.dumps(get_config("javascript")),
                     status=200,
                     mimetype="application/javascript")
    return resp

@app.route('/github')
def github():
    code = request.args.get('code')
    url = get_config('oauth/github/url') + code
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
    # query = db_session.query(User)
    # result = query.filter(User.uid == uid).first()
    # if (result == None):
    #     u = User(info['login'],uid,'github')
        # db_session.add(u)
        # db_session.commit()
    #print info
    return render_template("github.html",pic=info['id'],name=info['login'])

@app.route('/qq')
def qq():
    code = request.args.get('code')
    #print code
    url =  get_config("oauth/qq/url") + code + '&state=osslab'
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
    # query = db_session.query(User)
    # result = query.filter(User.uid == uid).first()
    #result = session.query(User).filter(User.uid == uid).all()
    # if (result == None):
    #     u = User(info['response']['name'],uid,'renren')
        # db_session.add(u)
        # db_session.commit()
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

    # url2 = config. APISERVER
    # data = urllib.urlencode(data)
    # req = urllib2.Request(url = url2 , data = data)
    # res_data = urllib2.urlopen(req)
    # res = 'http://' + res_data.read()
    return render_template("course.html",name=username,pic=url)

api.add_resource(CourseList, "/api/courses")
api.add_resource(DoCourse, "/api/course/<string:id>")
