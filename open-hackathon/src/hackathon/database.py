from . import UserMixin, app
import time
from flask.ext.sqlalchemy import SQLAlchemy
from functions import *
from datetime import datetime
import uuid, json

app.config["SQLALCHEMY_DATABASE_URI"] = safe_get_config("mysql/connection", "mysql://root:root@localhost/hackathon")
db = SQLAlchemy(app)


def to_json(inst, cls):
    # add your coversions for things like datetime's
    # and what-not that aren't serializable.
    convert = dict()
    convert[db.DateTime] = str

    d = dict()
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        if c.type.__class__ in convert.keys() and v is not None:
            try:
                func = convert[c.type.__class__]
                d[c.name] = func(v)
            except:
                d[c.name] = "Error:  Failed to covert using ", str(convert[c.type.__class__])
        elif v is None:
            d[c.name] = str()
        else:
            d[c.name] = v
    return json.dumps(d)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    nickname = db.Column(db.String(50))
    email = db.Column(db.String(100))
    openid = db.Column(db.String(100))
    avatar_url = db.Column(db.String(200))
    slug = db.Column(db.String(50), unique=True, nullable=False)  # can be used for branch name of github
    access_token = db.Column(db.String(100))
    create_time = db.Column(db.DateTime)
    last_login_time = db.Column(db.DateTime)

    def get_user_id(self):
        return self.id

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()
        if self.last_login_time is None:
            self.last_login_time = datetime.utcnow()
        if self.slug is None:
            self.slug = str(uuid.uuid1())[0:8]  # todo generate a real slug

    def __repr__(self):
        return "User: " + self.json()


class Register(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    register_name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    online = db.Column(db.Integer)  # 0:offline 1:online
    submitted = db.Column(db.Integer)  # 0:not 1:submitted
    create_time = db.Column(db.DateTime)
    submitted_time = db.Column(db.DateTime)
    description = db.Column(db.String(200))
    enabled = db.Column(db.Integer)  # 0: disabled 1:enabled
    jstrom_api = db.Column(db.String(50))
    jstrom_mgmt_portal = db.Column(db.String(50))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(Register, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()
        if self.enabled is None:
            self.enabled = 1
        self.online = 0
        self.submitted = 0

    def __repr__(self):
        return "Register:" + self.json()


class HostServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vm_name = db.Column(db.String(100), unique=True, nullable=False)
    public_dns = db.Column(db.String(50))
    public_cloudvm_port = db.Column(db.Integer)
    private_ip = db.Column(db.String(50), unique=True)
    private_cloudvm_port = db.Column(db.Integer)
    container_count = db.Column(db.Integer, nullable=False)
    container_max_count = db.Column(db.Integer, nullable=False)

    def json(self):
        return to_json(self, self.__class__)

    # e,g,:DockerHostServer('oss-docker-vm1', 'osslab1.chinacloudapp.cn', 8001, '10.207.250.79', 80, 0, 100)
    def __init__(self, **kwargs):
        super(HostServer, self).__init_(**kwargs)

    def __repr__(self):
        return "HostServer: " + self.json()


class Experiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))  # e.g.trial, real-time-analytics-hackathon
    vm_type = db.Column(db.String(50))  # e.g.docker, azure
    expr_name = db.Column(db.String(50))
    status = db.Column(db.Integer)  # 0=init 1=running 2=stopped 3=expr running 4=roll succeeded 5=rollback failed
    create_time = db.Column(db.DateTime)
    last_heart_beat_time = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('experiments', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(Experiment, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()
        if self.last_heart_beat_time is None:
            self.last_heart_beat_time = datetime.utcnow()

    def __repr__(self):
        return "Experiment: " + self.json()


class SCM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(20))
    branch = db.Column(db.String(50))
    repo_name = db.Column(db.String(50))
    repo_url = db.Column(db.String(100))
    local_repo_path = db.Column(db.String(100))
    create_time = db.Column(db.DateTime)

    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id', ondelete='CASCADE'))
    experiment = db.relationship('Experiment', backref=db.backref('scm', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(SCM, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()

    def __repr__(self):
        return "SCM: " + self.json()


class DockerContainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image = db.Column(db.String(50), nullable=False)
    container_id = db.Column(db.String(100))
    status = db.Column(db.Integer)  # 0=init 1=running 2=stopped 3=removed
    guacamole = db.Column(db.String(300))
    create_time = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('containers', lazy='dynamic'))

    host_server_id = db.Column(db.Integer, db.ForeignKey('host_server.id', ondelete='CASCADE'))
    host_server = db.relationship('HostServer', backref=db.backref('containers', lazy='dynamic'))

    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id', ondelete='CASCADE'))
    experiment = db.relationship('Experiment', backref=db.backref('containers', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(DockerContainer, self).__init__(**kwargs)
        self.status = 0
        if self.create_time is None:
            self.create_time = datetime.utcnow()


    def __repr__(self):
        return "DockerContainer:" + self.json()


class PortBinding(db.Model):
    # for simplicity, the port won't be released until the corresponding container removed(not stopped).
    # that means a port occupied by stopped container won't be allocated to new container. So it's possible to start the
    # container again. And the number of port should be enough since we won't have too many containers on the same VM.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    vm_public_port = db.Column(db.Integer)
    vm_private_port = db.Column(db.Integer, nullable=False)
    container_port = db.Column(db.Integer, nullable=False)

    host_server_id = db.Column(db.Integer, db.ForeignKey('host_server.id', ondelete='CASCADE'))
    host_server = db.relationship('HostServer', backref=db.backref('port_bindings', lazy='dynamic'))

    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id', ondelete='CASCADE'))
    experiment = db.relationship('Experiment', backref=db.backref('port_bindings', lazy='dynamic'))

    container_id = db.Column(db.Integer, db.ForeignKey('docker_container.id', ondelete='CASCADE'))
    container = db.relationship('DockerContainer', backref=db.backref('port_bindings', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(PortBinding, self).__init__(**kwargs)

    def __repr__(self):
        return "PortBinding: " + self.json()


class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200))
    enabled = db.Column(db.Integer)  # 1=enabled 0=disabled
    create_time = db.Column(db.DateTime)

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, content):
        self.content = content
        self.enabled = 1
        self.create_time = datetime.utcnow()

    def __repr__(self):
        return "Announcement: " + self.json()


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    create_time = db.Column(db.DateTime)

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, name):
        self.name = name
        self.create_time = datetime.utcnow()

    def __repr__(self):
        return "Role: " + self.json()


class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.DateTime)

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('roles', lazy='dynamic'))

    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))
    role = db.relationship('Role', backref=db.backref('users', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, role, user):
        self.role = role
        self.user = user
        self.create_time = datetime.utcnow()

    def __repr__(self):
        return "UserRole: " + self.json()
