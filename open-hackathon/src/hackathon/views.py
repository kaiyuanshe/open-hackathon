from datetime import timedelta
from os.path import realpath, dirname
import os

from flask import Response, render_template, url_for, g, abort
from flask_login import login_required, current_user
from flask_restful import Resource, reqparse

from . import app, api, login_manager
from expr import expr_manager
from user import user_manager
from database.models import Announcement
from user.login import *
from log import log
from database import db_adapter


session_lifetime_minutes = safe_get_config("login/session_minutes", 60)
PERMANENT_SESSION_LIFETIME = timedelta(minutes=session_lifetime_minutes)

Template_Routes = {
    "PrivacyStatement": "PrivacyStatement.html",
    "TermsOfUse": "TermsOfUse.html",
    'paper': "paper.html",
    "google": "google.html",
    "loading": "loading.html",
    "rightSide": "rightSide.html",
    "error": "error.html",
    "submitted": "submitted.html",
    "redirect": "redirect.html",
    "notregister": "notregister.html",
    "settings": "settings.html",
    "hackathon": "hackathon.html"
}


def simple_route(path):
    if Template_Routes.has_key(path):
        register = user_manager.get_registration_by_email(g.user.email)
        return render_template(Template_Routes[path], user=g.user, register=register)
    else:
        abort(404)


# login methods
@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=int(id)).first()


@app.route('/logout')
def logout():
    user_manager.logout(g.user)
    return redirect(url_for('index'))


@app.before_request
def before_request():
    g.user = current_user
    # session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=session_lifetime_minutes)


# index page
@app.route('/')
@app.route('/index')
def index():
    next = request.args.get("next")
    if next is not None:
        session["next"] = next
    return render_template("index.html", providers=safe_get_config("login/provider_enabled", ["github"]))


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
    # session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=session_lifetime_minutes)
    return simple_route(path)


# js config
@app.route('/config.js')
def js_config():
    resp = Response(response="var CONFIG=%s" % json.dumps(get_config("javascript")),
                    status=200,
                    mimetype="application/javascript")
    return resp


@app.route('/github')
def github():
    try:
        return GithubLogin().github_authorized()
    except Exception as err:
        log.error(err)
        return "Internal Server Error", 500


@app.route('/qq')
def qq():
    try:
        return QQLogin().qq_authorized()
    except Exception as err:
        log.error(err)
        return "Internal Server Error", 500


# @hackathon.route('/renren')
def renren():
    url_ori = request.url
    # if (url.ori.find('access_token') < 0) return render_template("renren.html",iden=url_ori,name='bb')
    if (len(url_ori) < 50):
        return render_template("renren.html", iden=url_ori, name='bb')
    start = url_ori.index('=')
    end = url_ori.index('&')
    # Str = request.query_string
    access_token = url_ori[start + 1:end]
    url = '/v2/user/get?access_token=' + access_token
    # httpres = query_info('api.renren.com',url,2)
    # #info = httpres.read()
    # info = json.loads(httpres.read())
    # name = 'renren' + str(info['response']['id'])
    # uid = str(uuid.uuid3(uuid.NAMESPACE_DNS,name))
    # query = db_session.query(User)
    # result = query.filter(User.uid == uid).first()
    # result = session.query(User).filter(User.uid == uid).all()
    # if (result == None):
    # u = User(info['response']['name'],uid,'renren')
    # db_session.add(u)
    # db_session.commit()
    # info = Str
    return render_template("renren.html")


class StatusList(Resource):
    # =======================================================return data start
    # [{"register_name":"zhang", "online":"1","submitted":"0"..."description":" "}]
    # =======================================================return data end
    def get(self):
        json_ret = map(lambda u: u.json(), user_manager.get_all_registration())
        return json_ret

    # =======================================================test data start
    # {"id":1, "online":1,"submitted":0}
    # =======================================================test data end
    def put(self):
        args = request.get_json()
        return expr_manager.submit_expr(args)


class DoCourse(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int)
        args = parser.parse_args()
        if 'id' not in args:
            return "Bad Request", 400

        cs = expr_manager.get_expr_status(args['id'])
        if cs is not None:
            return cs
        else:
            return "Not Found", 404

    def post(self):
        args = request.get_json()
        if "cid" not in args or "hackathon" not in args:
            return "invalid parameter", 400
        cid = args["cid"]
        hackathon = args["hackathon"]
        template_file = "%s/resources/%s-%s.js" % (dirname(realpath(__file__)), hackathon, cid)
        if os.path.isfile(template_file):
            # call remote service to start docker containers
            expr_config = json.load(file(template_file))
            try:
                return expr_manager.start_expr(hackathon, expr_config)
            except Exception as err:
                log.error(err)
                return "fail to start due to '%s'" % err, 500
        else:
            return "the experiment %s is not ready" % id, 404

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int)
        args = parser.parse_args()
        if 'id' not in args:
            return "Bad Request", 400

        return expr_manager.stop_expr(args["id"])

    def put(self):
        args = request.get_json()
        if "id" not in args:
            return "invalid parameter", 400
        return expr_manager.heart_beat(args["id"])


class Anmt(Resource):
    def get(self):
        return db_adapter.find_first_object(Announcement, enabled=1).json()


api.add_resource(DoCourse, "/api/course")
api.add_resource(StatusList, "/api/registerlist")
api.add_resource(Anmt, "/api/announcement")
