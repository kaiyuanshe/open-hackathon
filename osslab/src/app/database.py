from app import app
import time
from flask.ext.sqlalchemy import SQLAlchemy
from functions import *
from datetime import datetime
import uuid, json

app.config["SQLALCHEMY_DATABASE_URI"]= safe_get_config("mysql/connection", "mysql://root:root@localhost/hackathon")
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
                d[c.name] = convert[c.type.__class__](v)
            except:
                d[c.name] = "Error:  Failed to covert using ", str(convert[c.type.__class__])
        elif v is None:
            d[c.name] = str()
        else:
            d[c.name] = v
    return json.dumps(d)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    nickname = db.Column(db.String(50))
    email = db.Column(db.String(100))
    openid = db.Column(db.String(100))
    avatar_url = db.Column(db.String(200))
    slug = db.Column(db.String(50), unique=True, nullable=False) # can be used for branch name of github
    access_token = db.Column(db.String(100))
    create_time = db.Column(db.DateTime)
    last_login_time = db.Column(db.DateTime)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def is_admin(self):
        return self.admin.count() > 0

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, name, nickname, email, openid, avatar_url, access_token, slug=None, create_time=None, last_login_time=None):
        if create_time is None:
            create_time = datetime.utcnow()
        if last_login_time is None:
            last_login_time = datetime.utcnow()
        if slug is None:
            slug = str(uuid.uuid1())[0:8] # todo generate a real slug

        self.name = name
        self.nickname = nickname
        self.email = email
        self.openid = openid
        self.avatar_url = avatar_url
        self.slug = slug
        self.access_token = access_token
        self.create_time = create_time
        self.last_login_time = last_login_time

    def __repr__(self):
        return "User: " + self.json()


class Register(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    register_name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    online = db.Column(db.Integer) # 0:offline 1:online
    submitted = db.Column(db.Integer) # 0:not 1:submitted
    create_time = db.Column(db.DateTime)
    submitted_time = db.Column(db.DateTime)
    description = db.Column(db.String(200))
    enabled = db.Column(db.Integer)  # 0: disabled 1:enabled
    jstrom_api = db.Column(db.String(50))
    jstrom_mgmt_portal = db.Column(db.String(50))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, register_name, email, create_time=None, description=None, enabled=None):
        if create_time is None:
            create_time = datetime.utcnow()
        if enabled is None:
            enabled = 1

        self.register_name = register_name
        self.email = email
        self.online = 0
        self.submitted = 0
        self.create_time = create_time
        self.description = description
        self.enabled = enabled

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
    def __init__(self, vm_name, public_dns, public_cloudvm_port, private_ip, private_cloudvm_port, container_count, container_max_count):
        self.vm_name = vm_name
        self.public_dns = public_dns
        self.public_cloudvm_port = public_cloudvm_port
        self.private_ip = private_ip
        self.private_cloudvm_port = private_cloudvm_port
        self.container_count = container_count
        self.container_max_count = container_max_count

    def __repr__(self):
        return "HostServer: " + self.json()


class Experiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50)) #e.g.trial, real-time-analytics-hackathon
    vm_type = db.Column(db.String(50)) # e.g.docker, azure
    expr_name = db.Column(db.String(50))
    status = db.Column(db.Integer) # 0=init 1=running 2=stopped
    create_time = db.Column(db.DateTime)
    last_heart_beat_time = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('experiments', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, user, type, status, vm_type, expr_name, create_time=None, last_heart_beat_time=None):
        if create_time is None:
            create_time = datetime.utcnow()
        if last_heart_beat_time is None:
            last_heart_beat_time = datetime.utcnow()

        self.user = user
        self.type = type
        self.vm_type = vm_type
        self.expr_name = expr_name
        self.status = status
        self.create_time = create_time
        self.last_heart_beat_time = last_heart_beat_time

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

    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id'))
    experiment = db.relationship('Experiment', backref=db.backref('scm', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, experiment, provider, branch, repo_name, repo_url, local_repo_path=None, create_time=None):
        if create_time is None:
            create_time = datetime.utcnow()

        self.experiment = experiment
        self.provider = provider
        self.branch = branch
        self.repo_name = repo_name
        self.repo_url = repo_url
        self.local_repo_path = local_repo_path
        self.create_time = create_time

    def __repr__(self):
        return "SCM: " + self.json()


class DockerContainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image = db.Column(db.String(50), nullable=False)
    container_id = db.Column(db.String(100))
    status = db.Column(db.Integer) # 0=init 1=running 2=stopped 3=removed
    guacamole = db.Column(db.String(300))
    create_time= db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('containers', lazy='dynamic'))

    host_server_id = db.Column(db.Integer, db.ForeignKey('host_server.id'))
    host_server = db.relationship('HostServer', backref=db.backref('containers', lazy='dynamic'))

    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id'))
    experiment = db.relationship('Experiment', backref=db.backref('containers', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, name, user, host_server, experiment, image, create_time=None):
        self.name = name
        self.user = user
        self.host_server = host_server
        self.experiment= experiment
        self.image= image
        self.status= 0
        self.create_time= create_time if create_time is not None else datetime.utcnow()

    def __repr__(self):
        return "DockerContainer:" + self.json()


class PortBinding(db.Model):
    # for simplicity, the port won't be released until the corresponding container removed(not stopped).
    # that means a port occupied by stopped container won't be allocated to new container. So it's possible to start the
    # container again. And the number of port should be enough since we won't have too many containers on the same VM.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    vm_public_port= db.Column(db.Integer)
    vm_private_port= db.Column(db.Integer, nullable=False)
    container_port= db.Column(db.Integer, nullable=False)

    host_server_id = db.Column(db.Integer, db.ForeignKey('host_server.id'))
    host_server = db.relationship('HostServer', backref=db.backref('port_bindings', lazy='dynamic'))

    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id'))
    experiment = db.relationship('Experiment', backref=db.backref('port_bindings', lazy='dynamic'))

    container_id = db.Column(db.Integer, db.ForeignKey('docker_container.id'))
    container = db.relationship('DockerContainer', backref=db.backref('port_bindings', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, name, vm_public_port, vm_private_port, container_port, host_server, experiment, container):
        self.name = name
        self.vm_public_port = vm_public_port
        self.vm_private_port = vm_private_port
        self.container_port = container_port
        self.host_server = host_server
        self.experiment = experiment
        self.container = container

    def __repr__(self):
        return "PortBinding: " + self.json()


class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200))
    enabled = db.Column(db.Integer) # 1=enabled 0=disabled
    create_time= db.Column(db.DateTime)

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, content):
        self.content = content
        self.enabled = 1
        self.create_time = datetime.utcnow()

    def __repr__(self):
        return "Announcement: " + self.json()


# temporary class
class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('admin', lazy='dynamic'), uselist=False)

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, user):
        self.user = user

    def __repr__(self):
        return "AdminUser: " + self.json()