import sys

sys.path.append("..")
from flask import redirect, request, url_for, g
from hackathon import app
from flask_admin import BaseView, expose, Admin, AdminIndexView
from hackathon.decorators import role_required
from hackathon.constants import ADMIN, HOST


class HomeView(AdminIndexView):
    @expose('/')
    def index(self):
        if not g.user.is_authenticated():
            return redirect(url_for('index', next=request.path))
        if not g.user.has_roles((ADMIN, HOST)):
            return redirect("/hackathon")
        return self.render('admin/index.html', user=g.user)


class OsslabBaseView(BaseView):
    def render_admin(self, template):
        return self.render("admin/%s" % template)


class MyAdminView(OsslabBaseView):
    @expose('/')
    def index(self):
        return self.render_admin('myadmin.html')

    @role_required(ADMIN)
    def is_accessible(self):
        return True


class AnotherAdminView(OsslabBaseView):
    @expose('/')
    def index(self):
        return self.render_admin('anotheradmin.html')

    @expose('/test/')
    def test(self):
        return self.render_admin('test.html')

    @role_required([ADMIN, HOST])
    def is_accessible(self):
        return True


admin = Admin(name="Open Hackathon Admin Console",
              base_template='admin/osslayout.html',
              index_view=HomeView())
admin.init_app(app)

admin.add_view(MyAdminView(name="view1", category='Test'))
admin.add_view(AnotherAdminView(name="view2", category='Test'))
