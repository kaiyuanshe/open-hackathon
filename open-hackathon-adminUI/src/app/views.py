import sys

sys.path.append("..")
from flask import redirect, request, url_for, g
from app import app
from flask_admin import BaseView, expose, Admin, AdminIndexView
from decorators import role_required
from constants import ROLE


class HomeView(AdminIndexView):
    @expose('/')
    def index(self):
        #if not g.user.is_authenticated():
        #    return redirect(url_for('index', next=request.path))
        #if not g.user.has_roles((ROLE.ADMIN, ROLE.HOST)):

        #    return redirect("/hackathon")
        return self.render('admin/index.html')


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
