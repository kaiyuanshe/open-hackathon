import sys

sys.path.append("..")
from . import UserMixin
from . import db
from datetime import datetime
import uuid
import json


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
    email = db.Column(db.String(50))
    openid = db.Column(db.String(100))
    avatar_url = db.Column(db.String(200))
    slug = db.Column(db.String(50), unique=True, nullable=False)  # can be used for branch name of github
    access_token = db.Column(db.String(100))
    online = db.Column(db.Integer)  # 0:offline 1:online
    create_time = db.Column(db.DateTime)
    last_login_time = db.Column(db.DateTime)

    def get_user_id(self):
        return self.id

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, name, nickname, email, openid, avatar_url, access_token, online=0, slug=None, create_time=None,
                 last_login_time=None):
        if create_time is None:
            create_time = datetime.utcnow()
        if last_login_time is None:
            last_login_time = datetime.utcnow()
        if slug is None:
            slug = str(uuid.uuid1())[0:8]  # todo generate a real slug

        self.name = name
        self.nickname = nickname
        self.email = email
        self.openid = openid
        self.avatar_url = avatar_url
        self.slug = slug
        self.online = online
        self.access_token = access_token
        self.create_time = create_time
        self.last_login_time = last_login_time

    def __repr__(self):
        return "User: " + self.json()


class Register(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    register_name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    create_time = db.Column(db.DateTime)
    description = db.Column(db.String(200))
    enabled = db.Column(db.Integer)  # 0: disabled 1:enabled
    jstrom_api = db.Column(db.String(50))
    jstrom_mgmt_portal = db.Column(db.String(50))

    hackathon_id = db.Column(db.Integer, db.ForeignKey('hackathon.id', ondelete='CASCADE'))
    hackathon = db.relationship('Hackathon', backref=db.backref('registers', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, hackathon, register_name, email, create_time=None, description=None, enabled=None):
        if create_time is None:
            create_time = datetime.utcnow()
        if enabled is None:
            enabled = 1

        self.hackathon = hackathon
        self.register_name = register_name
        self.email = email
        self.submitted = 0
        self.create_time = create_time
        self.description = description
        self.enabled = enabled

    def __repr__(self):
        return "Register:" + self.json()


class Hackathon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    sponsor = db.Column(db.Integer)
    status = db.Column(db.Integer)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    create_time = db.Column(db.DateTime)

    def json(self):
        return to_json(self, self.__class__)

    # e,g,:DockerHostServer('oss-docker-vm1', 'osslab1.chinacloudapp.cn', 8001, '10.207.250.79', 80, 0, 100)
    def __init__(self, name, sponsor, create_time=None):
        if create_time is None:
            create_time = datetime.utcnow()
        self.name = name
        self.sponsor = sponsor
        self.create_time = create_time

    def __repr__(self):
        return "Hackathon: " + self.json()


class DockerHostServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vm_name = db.Column(db.String(100), unique=True, nullable=False)
    public_dns = db.Column(db.String(50))
    public_docker_api_port = db.Column(db.Integer)
    private_ip = db.Column(db.String(50), unique=True)
    private_docker_api_port = db.Column(db.Integer)
    container_count = db.Column(db.Integer, nullable=False)
    container_max_count = db.Column(db.Integer, nullable=False)

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, vm_name, public_dns, public_docker_api_port, private_ip, private_docker_api_port,
                 container_count=0,
                 container_max_count=0):
        self.vm_name = vm_name
        self.public_dns = public_dns
        self.public_docker_api_port = public_docker_api_port
        self.private_ip = private_ip
        self.private_docker_api_port = private_docker_api_port
        self.container_count = container_count
        self.container_max_count = container_max_count

    def __repr__(self):
        return "HostServer: " + self.json()


class Experiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer)  # see enum.py
    create_time = db.Column(db.DateTime)
    last_heart_beat_time = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('experiments', lazy='dynamic'))

    hackathon_id = db.Column(db.Integer, db.ForeignKey('hackathon.id', ondelete='CASCADE'))
    hackathon = db.relationship('Hackathon', backref=db.backref('experiments', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, user, hackathon, status, create_time=None, last_heart_beat_time=None):
        if create_time is None:
            create_time = datetime.utcnow()
        if last_heart_beat_time is None:
            last_heart_beat_time = datetime.utcnow()

        self.user = user
        self.hackathon = hackathon
        self.status = status
        self.create_time = create_time
        self.last_heart_beat_time = last_heart_beat_time

    def __repr__(self):
        return "Experiment: " + self.json()


class VirtualEnvironment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100))
    status = db.Column(db.Integer)  # see enum.py
    remote_provider = db.Column(db.String(20))
    remote_paras = db.Column(db.String(300))
    create_time = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('virtual_environments', lazy='dynamic'))

    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id', ondelete='CASCADE'))
    experiment = db.relationship('Experiment', backref=db.backref('virtual_environments', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, provider, name, image, status, remote_provider, user, experiment, create_time=None):
        if create_time is None:
            create_time = datetime.utcnow()

        self.provider = provider
        self.name = name
        self.image = image
        self.status = status
        self.remote_provider = remote_provider
        self.status = status
        self.create_time = create_time
        self.user = user
        self.experiment = experiment

    def __repr__(self):
        return "VirtualEnvironment: " + self.json()


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


# detail info of a VirtualEnvironment in case Docker
class DockerContainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image = db.Column(db.String(50), nullable=False)
    container_id = db.Column(db.String(100))
    create_time = db.Column(db.DateTime)

    virtual_environment_id = db.Column(db.Integer, db.ForeignKey('virtual_environment.id', ondelete='CASCADE'))
    virtual_environment = db.relationship(VirtualEnvironment,
                                          backref=db.backref('container', uselist=False))

    host_server_id = db.Column(db.Integer, db.ForeignKey('docker_host_server.id', ondelete='CASCADE'))
    host_server = db.relationship('DockerHostServer', backref=db.backref('containers', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, name, host_server, virtual_environment, experiment, image, create_time=None):
        self.name = name
        self.host_server = host_server
        self.virtual_environment = virtual_environment
        self.experiment = experiment
        self.image = image
        self.create_time = create_time if create_time is not None else datetime.utcnow()

    def __repr__(self):
        return "DockerContainer:" + self.json()


class PortBinding(db.Model):
    # for simplicity, the port won't be released until the corresponding container removed(not stopped).
    # that means a port occupied by stopped container won't be allocated to new container. So it's possible to start the
    # container again. And the number of port should be enough since we won't have too many containers on the same VM.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    port_from = db.Column(db.Integer, nullable=False)
    port_to = db.Column(db.Integer, nullable=False)
    binding_type = db.Column(db.Integer)  # CloudService or Docker, see enum.py
    binding_resource_id = db.Column(
        db.Integer)  # DockerHostServer.id if binding_type is Docker, VM resource id if cloudservice

    virtual_environment_id = db.Column(db.Integer, db.ForeignKey('virtual_environment.id', ondelete='CASCADE'))
    virtual_environment = db.relationship('VirtualEnvironment', backref=db.backref('port_bindings', lazy='dynamic'))

    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id', ondelete='CASCADE'))
    experiment = db.relationship('Experiment', backref=db.backref('port_bindings', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, name, port_from, port_to, binding_type, binding_resource_id, virtual_environment, experiment):
        self.name = name
        self.port_from = port_from
        self.port_to = port_to
        self.binding_type = binding_type
        self.binding_resource_id = binding_resource_id
        self.virtual_environment = virtual_environment
        self.experiment = experiment

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
