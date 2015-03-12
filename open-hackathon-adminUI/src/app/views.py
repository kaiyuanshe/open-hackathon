
from . import app
from flask_admin import BaseView, expose, Admin, AdminIndexView
from decorators import role_required
from constants import ROLE
from functions import get_config
import json

from flask_login import login_required, current_user,login_user,LoginManager
from admin.login import login_providers
from flask import Response, render_template, request, g, redirect, make_response
from database.models import AdminUser
from database import db_adapter
from datetime import timedelta


session_lifetime_minutes = 60
PERMANENT_SESSION_LIFETIME = timedelta(minutes=session_lifetime_minutes)


login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(id):
    return db_adapter.find_first_object(AdminUser,id=id)


@app.before_request
def before_request():
    g.admin = current_user
    app.permanent_session_lifetime = timedelta(minutes=session_lifetime_minutes)


class HomeView(AdminIndexView):
    @login_required
    @expose('/')
    def index(self):
        #if not g.user.is_authenticated():
        #    return redirect(url_for('index', next=request.path))
        #if not g.user.has_roles((ROLE.ADMIN, ROLE.HOST)):

        #    return redirect("/hackathon")
        return self.render('admin/home.html')


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


admin = Admin(name="Open Hackathon Admin Console",base_template='admin/osslayout.html',index_view=HomeView())
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
    login_user(login_result)
    return make_response(redirect("/admin"))


@app.route('/github')
def github_login():
    return __login("github")


@app.route('/qq')
def qq_login():
    return __login("qq")


@app.route('/')
@app.route('/index')
def index():
    return render_template('/admin/login.html')


@app.route("/logout")
@login_required
def logout():
    login_providers.values()[0].logout(g.admin)
    return redirect("/index")