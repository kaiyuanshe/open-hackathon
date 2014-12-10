import uuid
from flask import request, Response, render_template, flash, redirect, session, url_for, g
from flask.ext.restful import Api, Resource
from app import app
from functions import *
from routes import *
from database import User
from login import *
from constants import *
from log import log
from flask.ext.login import login_required, LoginManager, logout_user, current_user
from datetime import timedelta

app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(days=1)
api = Api(app)
login_manager = LoginManager()
login_manager.login_view = "index"
login_manager.login_message_category = "info"
login_manager.setup_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=int(id)).first()

# index page
@app.route('/')
@app.route('/index')
def index():
    session.permanent = False
    return render_template("index.html")

# error handler for 404
@app.errorhandler(404)
def page_not_found(error):
    # render a beautiful 404 page
    log.error(error)
    return "Page not Found", 404

# error handler for 500
@app.errorhandler(500)
def internal_error(error):
    # render a beautiful 500 page
    log.error(error)
    return "Internal Server Error", 500

# simple webPages. login required
@app.route('/<path:path>')
@login_required
def template_routes(path):
    return simple_route(path)

# js config
@app.route('/config.js')
def js_config():
    resp =  Response(response="var CONFIG=%s" % json.dumps(get_config("javascript")),
                     status=200,
                     mimetype="application/javascript")
    return resp

@app.route('/notregister')
def not_registered():
    return render_template("notregister.html")

@app.route('/settings')
@login_required
def hackathon_settings():
    return render_template("settings.html", name=g.user.nickname, pic=g.user.avatar_url)

@app.route('/hackathon')
@login_required
def hackathon():
    return render_template("hackathon.html", name=g.user.nickname, pic=g.user.avatar_url)

@app.route('/github')
def github():
    code = request.args.get('code')
    gl = GithubLogin()
    user = gl.github_authorized(code)
    if user is not None:
        expr = Experiment.query.filter(Experiment.user_id == user.id).first()
        if expr is not None and expr.status == 1:
            reg = Register.query.filter(Register.email == user.email).first()
            if reg is not None and reg.submitted == 1:
                return redirect("/submitted")
            else:
                return redirect("/hackathon")
        else:
            return redirect("/settings")
    else:
        return redirect("/notregister")

@app.route('/qq')
def qq():
    code = request.args.get('code')
    state = request.args.get('state')
    if state != QQ_OAUTH_STATE:
        log.warn("STATE match fail. Potentially CSFR.")
        return "UnAuthorized", 401

    qq_login = QQLogin()
    user = qq_login.qq_authorized(code, state)
    log.info("qq user login successfully:" + repr(user))

    return redirect("/settings")

# @app.route('/renren')
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
    # httpres = query_info('api.renren.com',url,2)
    # #info = httpres.read()
    # info = json.loads(httpres.read())
    # name = 'renren' + str(info['response']['id'])
    # uid = str(uuid.uuid3(uuid.NAMESPACE_DNS,name))
    # query = db_session.query(User)
    # result = query.filter(User.uid == uid).first()
    #result = session.query(User).filter(User.uid == uid).all()
    # if (result == None):
    #     u = User(info['response']['name'],uid,'renren')
        # db_session.add(u)
        # db_session.commit()
    #info = Str
    return render_template("renren.html")
    #return render_template("renren.html",iden=url_ori,name='cc')
    # return render_template("renren.html",pic = info['response']['avatar'][0]['url'],name=info['response']['name'])

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.before_request
def before_request():
    g.user = current_user

api.add_resource(CourseList, "/api/courses")
api.add_resource(DoCourse, "/api/course/<string:id>")
api.add_resource(StatusList, "/api/registerlist")
