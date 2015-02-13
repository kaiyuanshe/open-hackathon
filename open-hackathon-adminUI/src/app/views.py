import sys

sys.path.append("..")
from flask import redirect, request, url_for, g
from app import app
from flask_admin import BaseView, expose, Admin, AdminIndexView
from decorators import role_required
from constants import ROLE
from functions import get_config , delete_remote, get_remote, safe_get_config
import json

###########
from flask_login import login_required, current_user, logout_user, login_user
from admin.login import login_providers, LoginUser
from flask import Response, render_template, abort, request, session, g, redirect, make_response







class IndexView(AdminIndexView):
    @expose('/')
    def index(self):
        #if not g.user.is_authenticated():
        #    return redirect(url_for('index', next=request.path))
        #if not g.user.has_roles((ROLE.ADMIN, ROLE.HOST)):

        #    return redirect("/hackathon")
        return self.render('admin/login.html')


class HackathonAdminBaseView(BaseView):
    def render_admin(self, template):
        return self.render("admin/%s" % template)


class MyAdminView(HackathonAdminBaseView):
    @expose('/')
    def index(self):
        return self.render_admin('myadmin.html')

    @role_required(ROLE.ADMIN)
    def is_accessible(self):
        return True


class AnotherAdminView(HackathonAdminBaseView):
    @expose('/')
    def index(self):
        return self.render_admin('anotheradmin.html')

    @expose('/test/')
    def test(self):
        return self.render_admin('test.html')

    @role_required([ROLE.ADMIN, ROLE.HOST])
    def is_accessible(self):
        return True




admin = Admin(name="Open Hackathon Admin Console",index_view=IndexView())
admin.init_app(app)

admin.add_view(MyAdminView(name="view1", category='Test'))
admin.add_view(AnotherAdminView(name="view2", category='Test'))

###############################################################################################


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

    if login_result["register_state"] == False:
        response = make_response(redirect("notregister"))
    else:
        if len(login_result['experiments']) > 0:
            response = make_response(redirect("hackathon"))
        else:
            response = make_response(redirect("settings"))
        response.set_cookie('token', login_result["token"])

    return response



@app.route('/github')
def github_login():
    return __login("github")

