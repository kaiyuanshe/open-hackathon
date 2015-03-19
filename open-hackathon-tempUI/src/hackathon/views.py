from flask import Response, render_template, abort, request, session, g, redirect, make_response
from . import *
from log import log
import json
from functions import get_config, delete_remote, get_remote, safe_get_config
from login import login_providers, LoginUser
from flask_login import login_required, current_user, logout_user, login_user
from datetime import timedelta
from flask import make_response

session_lifetime_minutes = 60
PERMANENT_SESSION_LIFETIME = timedelta(minutes=session_lifetime_minutes)

Template_Routes = {
    "PrivacyStatement": "PrivacyStatement.html",
    "TermsOfUse": "TermsOfUse.html",
    "error": "error.html",
    "submitted": "submitted.html",
    "redirect": "redirect.html",
    "notregister": "notregister.html",
    "challenges":"challenges.html"
}


@login_manager.user_loader
def load_user(id):
    try:
        ur = get_remote("%s/api/user?uid=%d" % (get_config("hackathon-api.endpoint"), int(id)))
        ur = json.loads(ur)
        return LoginUser(id=ur["id"], name=ur["name"], nickname=ur["nickname"], avatar_url=ur["avatar_url"])
    except Exception as e:
        log.error(e)
        return None


@app.before_request
def before_request():
    g.user = current_user
    app.permanent_session_lifetime = timedelta(minutes=session_lifetime_minutes)


def simple_route(path):
    if Template_Routes.has_key(path):
        return render_template(Template_Routes[path])
    else:
        log.warn("page '%s' not found" % path)
        abort(404)


# index page
@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
                           providers=safe_get_config("login.provider_enabled", ["github", "qq", "gitcafe","weibo"]),
                           meta_content={'weibo':get_config('login.weibo.meta_content'),
                                         'qq':get_config('login.qq.meta_content')})


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


@app.route('/<path:path>')
def template_routes(path):
    return simple_route(path)


@app.route('/settings')
@login_required
def settings():
    if not session["register_state"]:
        return redirect("notregister")

    return render_template("settings.html")


@app.route('/hackathon')
@login_required
def hackathon():
    if not session["register_state"]:
        return redirect("notregister")

    return render_template("hackathon.html")


# js config
@app.route('/config.js')
def js_config():
    resp = Response(response="var CONFIG=%s" % json.dumps(get_config("javascript")),
                    status=200,
                    mimetype="application/javascript")
    return resp


def __login(provider):
    code = request.args.get('code')
    login_result = login_providers[provider].login({
        "code": code
    })
    user = LoginUser(id=login_result["id"],
                     name=login_result["name"],
                     avatar_url=login_result["avatar_url"],
                     nickname=login_result["nickname"])
    login_user(user)

    session["token"] = login_result["token"]
    session["register_state"] = login_result["register_state"]

    if not login_result["register_state"]:
        response = make_response(redirect("notregister"))
    else:
        if len(login_result['experiments']) > 0:
            response = make_response(redirect("hackathon"))
        else:
            response = make_response(redirect("settings"))
        response.set_cookie('token', login_result["token"])

    return response


@app.route('/qq')
def qq_login():
    return __login("qq")


@app.route('/github')
def github_login():
    return __login("github")


@app.route('/gitcafe')
def gitcafe_login():
    return __login("gitcafe")


@app.route('/weibo')
def weibo_login():
    return __login("weibo")

@app.route("/logout")
@login_required
def logout():
    url = "%s/api/user/login?uid=%d" % (get_config("hackathon-api.endpoint"), g.user.id)
    delete_remote(url, {
        "token": session["token"]
    })
    session.pop("token")
    logout_user()
    return redirect("index")