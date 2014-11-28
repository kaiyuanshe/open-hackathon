import uuid


from flask import request, Response,render_template, flash, redirect, session, url_for, g
from flask.ext.restful import Api, Resource
from app import app,oid
# from app import app
from functions import *
from routes import *
from database import *
from flask.ext.login import  login_required


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

    emailUrl = '/user/emails?access_token=' + access_token
    conn.request('GET',emailUrl,'',{'user-agent':'flask'})
    httpres = conn.getresponse()
    emailList = json.loads(httpres.read())
    if(len(emailList)>1):
        for data in emailList:
            if(data.get("primary")):
                useremail=data.get("email")
                break
    else:
        useremail=emailList[0].get("email")

    session['email'] = useremail
    user = User.query.filter_by(email=useremail).first()

    if (user == None):
        u = User(info['login'],useremail)
        db.session.add(u)
        db.session.commit()

    else:
        g.user = user

    # query = db_session.query(User)
    # result = query.filter(User.uid == uid).first()
    # if (result == None):
    #     u = User(info['login'],uid,'github')
    #     db_session.add(u)
    #     db_session.commit()
    #print info


    return render_template("github.html",pic=info['avatar_url'],name=info['login'])

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

# @app.route('/course')
# def course():
#     typecode = request.args.get('type')
#     username = request.cookies.get('username')
#     url = request.cookies.get('picurl')
#     data = mapper(int(typecode),username)
#
#     # url2 = config. APISERVER
#     # data = urllib.urlencode(data)
#     # req = urllib2.Request(url = url2 , data = data)
#     # res_data = urllib2.urlopen(req)
#     # res = 'http://' + res_data.read()
#     return render_template("course.html",name=username,pic=url)

# @lm.user_loader
# def load_user(id):
#     return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = None
    if 'email' in session:
        email = session['email']
        g.user = User.query.filter_by(email=email).first()

@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None:
        # return redirect(url_for('index'))
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
        if openid:
            return oid.try_login(openid, ask_for=['name'])
    return render_template('index.html', next=oid.get_next_url(),
                           error=oid.fetch_error())
    # return render_template('github.html')


@oid.after_login
def after_login(resp):
    session['openid'] = resp.identity_url
    user = User.query.filter_by(uid=resp.identity_url).first()
    if user is not None:

        g.user = user
        return redirect(oid.get_next_url())
    return redirect(url_for('create_profile', next=oid.get_next_url(),
                            name=resp.name or resp.nickname,
                            email=resp.email))
    # return redirect(request.args.get('next') or url_for('index'))


# @app.route('/create-profile', methods=['GET', 'POST'])
# def create_profile():
#     if g.user is not None or 'openid' not in session:
#         return redirect(url_for('index'))
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         if not name:
#             flash(u'Error: you have to provide a name')
#         elif '@' not in email:
#             flash(u'Error: you have to enter a valid email address')
#         else:
#             flash(u'Profile successfully created')
#             db_session.add(User(name, session['openid']))
#             db_session.commit()
#             return redirect(oid.get_next_url())
#     return render_template('create_profile.html', next=oid.get_next_url())




api.add_resource(CourseList, "/api/courses")
api.add_resource(DoCourse, "/api/course/<string:name>")
