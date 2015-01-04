from app import app
from flask.ext.admin import BaseView, expose, Admin, AdminIndexView
from flask import g, redirect, request, url_for
from app.database import AdminUser, User, db


class HomeView(AdminIndexView):
    @expose('/')
    def index(self):
        if not g.user.is_authenticated():
            return redirect(url_for('index', next=request.path))
        if not g.user.is_admin():
            return redirect("/hackathon")
        return self.render('admin/index.html', user=g.user)


class OsslabBaseView(BaseView):
    def render_admin(self, template):
        return self.render("admin/%s" % template)

    def is_accessible(self):
        return g.user.is_authenticated() and g.user.is_admin()


class MyAdminView(OsslabBaseView):
    @expose('/')
    def index(self):
        return self.render_admin('myadmin.html')


class AnotherAdminView(OsslabBaseView):
    @expose('/')
    def index(self):
        return self.render_admin('anotheradmin.html')

    @expose('/test/')
    def test(self):
        return self.render_admin('test.html')


admin = Admin(name="Open Hackathon Admin Console",
              base_template='admin/osslayout.html',
              index_view=HomeView())
admin.init_app(app)

admin.add_view(MyAdminView(name="view1", category='Test'))
admin.add_view(AnotherAdminView(name="view2", category='Test'))

# make the first login user be the first admin
def create_first_admin():
    if AdminUser.query.count() == 0:
        first_admin = AdminUser(User.query.first())
        db.session.add(first_admin)
        db.session.commit()

create_first_admin()