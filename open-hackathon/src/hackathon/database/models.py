import sys
import email
import os

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
    convert[db.DateTime] = long

    d = dict()
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        if c.type.__class__ in convert.keys() and v is not None:
            try:
                func = convert[c.type.__class__]
                d[c.name] = func((v - datetime(1970, 1, 1)).total_seconds() * 1000)
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


class UserEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120))
    primary_email = db.Column(db.Integer)  # 0:NOT Primary Email 1:Primary Email
    verified = db.Column(db.Integer)  # 0 for not verified, 1 for verified

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('emails', lazy='dynamic'))

    def get_user_email(self):
        return self.email(self, email)

    def __init__(self, **kwargs):
        super(UserEmail, self).__init__(**kwargs)


class UserToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(50), unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('tokens', lazy='dynamic'))

    issue_date = db.Column(db.DateTime)
    expire_date = db.Column(db.DateTime, nullable=False)

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, token, user, expire_date, issue_date=None):
        if issue_date is None:
            issue_date = datetime.utcnow()

        self.token = token
        self.user = user
        self.expire_date = expire_date
        self.issue_date = issue_date

    def __repr__(self):
        return "UserToken: " + self.json()


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

    def __init__(self, **kwargs):
        super(Register, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()
        if self.enabled is None:
            self.enabled = 1
        self.online = 0

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

    def __init__(self, **kwargs):
        super(Hackathon, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()

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

    def __init__(self, **kwargs):
        super(DockerHostServer, self).__init__(**kwargs)

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

    # adaptor for auto azure deploy
    user_template_id = db.Column(db.Integer, db.ForeignKey('user_template.id', ondelete='CASCADE'))
    user_template = db.relationship('UserTemplate', backref=db.backref('experiments', lazy='dynamic'))

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

    def __init__(self, **kwargs):
        super(VirtualEnvironment, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()

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

    def __init__(self, **kwargs):
        super(SCM, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()

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

    def __init__(self, exper, **kwargs):
        self.experiment = exper
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


class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    url = db.Column(db.String(200))  # backup, templates' location
    provider = db.Column(db.String(20))
    create_time = db.Column(db.DateTime)

    hackathon_id = db.Column(db.Integer, db.ForeignKey('hackathon.id', ondelete='CASCADE'))
    hackathon = db.relationship('Hackathon', backref=db.backref('templates', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(Template, self).__init__(**kwargs)

        if self.provider is None:
            self.provider = "docker"
        self.create_time = datetime.utcnow()

    def __repr__(self):
        return "Template: " + self.json()


# ------------------------------ Tables are introduced by azure-auto-deploy ------------------------------


class UserTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.DateTime)
    last_modify_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('user_template', lazy='dynamic'))
    template_id = db.Column(db.Integer, db.ForeignKey('template.id', ondelete='CASCADE'))
    template = db.relationship('Template', backref=db.backref('user_template', lazy='dynamic'))

    def __init__(self, user, template, create_time=None, last_modify_time=None):
        if create_time is None:
            create_time = datetime.utcnow()
        if last_modify_time is None:
            last_modify_time = datetime.utcnow()
        self.user = user
        self.template = template
        self.create_time = create_time
        self.last_modify_time = last_modify_time


class UserOperation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operation = db.Column(db.String(50))
    status = db.Column(db.String(50))
    note = db.Column(db.String(500))
    exec_time = db.Column(db.DateTime)
    user_template_id = db.Column(db.Integer, db.ForeignKey('user_template.id', ondelete='CASCADE'))
    user_template = db.relationship('UserTemplate', backref=db.backref('user_operation', lazy='dynamic'))

    def __init__(self, user_template, operation, status, note=None, exec_time=None):
        if exec_time is None:
            exec_time = datetime.utcnow()
        self.user_template = user_template
        self.operation = operation
        self.status = status
        self.note = note
        self.exec_time = exec_time

    def json(self):
        return to_json(self, self.__class__)

    def __repr__(self):
        return "UserOperation: " + self.json()


class UserResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    name = db.Column(db.String(50))
    status = db.Column(db.String(50))
    create_time = db.Column(db.DateTime)
    last_modify_time = db.Column(db.DateTime)
    user_template_id = db.Column(db.Integer, db.ForeignKey('user_template.id', ondelete='CASCADE'))
    user_template = db.relationship('UserTemplate', backref=db.backref('user_resource1', lazy='dynamic'))
    # for deployment and virtual machine
    cloud_service_id = db.Column(db.Integer, db.ForeignKey('user_resource.id', ondelete='CASCADE'))

    def __init__(self, user_template, type, name, status, cloud_service_id, create_time=None, last_modify_time=None):
        if create_time is None:
            create_time = datetime.utcnow()
        if last_modify_time is None:
            last_modify_time = datetime.utcnow()
        self.user_template = user_template
        self.type = type
        self.name = name
        self.status = status
        self.cloud_service_id = cloud_service_id
        self.create_time = create_time
        self.last_modify_time = last_modify_time

    def json(self):
        return to_json(self, self.__class__)

    def __repr__(self):
        return "UserResource: " + self.json()


class VMEndpoint(db.Model):
    __tablename__ = 'vm_endpoint'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    protocol = db.Column(db.String(50))
    public_port = db.Column(db.Integer)
    private_port = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)
    last_modify_time = db.Column(db.DateTime)
    cloud_service_id = db.Column(db.Integer, db.ForeignKey('user_resource.id', ondelete='CASCADE'))
    cloud_service = db.relationship('UserResource', foreign_keys=[cloud_service_id],
                                    backref=db.backref('vm_endpoint1', lazy='dynamic'))
    virtual_machine_id = db.Column(db.Integer, db.ForeignKey('user_resource.id', ondelete='CASCADE'))
    virtual_machine = db.relationship('UserResource', foreign_keys=[virtual_machine_id],
                                      backref=db.backref('vm_endpoint2', lazy='dynamic'))

    def __init__(self, name, protocol, public_port, private_port, cloud_service, virtual_machine=None,
                 create_time=None, last_modify_time=None):
        if create_time is None:
            create_time = datetime.utcnow()
        if last_modify_time is None:
            last_modify_time = datetime.utcnow()
        self.cloud_service = cloud_service
        self.virtual_machine = virtual_machine
        self.name = name
        self.protocol = protocol
        self.public_port = public_port
        self.private_port = private_port
        self.create_time = create_time
        self.last_modify_time = last_modify_time

    def json(self):
        return to_json(self, self.__class__)

    def __repr__(self):
        return "VMEndpoint: " + self.json()


class VMConfig(db.Model):
    __tablename__ = 'vm_config'
    id = db.Column(db.Integer, primary_key=True)
    dns = db.Column(db.String(50))
    public_ip = db.Column(db.String(50))
    private_ip = db.Column(db.String(50))
    create_time = db.Column(db.DateTime)
    last_modify_time = db.Column(db.DateTime)
    virtual_machine_id = db.Column(db.Integer, db.ForeignKey('user_resource.id', ondelete='CASCADE'))
    virtual_machine = db.relationship('UserResource', backref=db.backref('vm_config1', lazy='dynamic'))
    remote_provider = db.Column(db.String(20))
    remote_paras = db.Column(db.String(300))
    user_template_id = db.Column(db.Integer, db.ForeignKey('user_template.id', ondelete='CASCADE'))
    user_template = db.relationship('UserTemplate', backref=db.backref('vm_config2', lazy='dynamic'))

    def __init__(self, virtual_machine, dns, public_ip, private_ip,
                 remote_provider, remote_paras, user_template,
                 create_time=None, last_modify_time=None):
        if create_time is None:
            create_time = datetime.utcnow()
        if last_modify_time is None:
            last_modify_time = datetime.utcnow()
        self.virtual_machine = virtual_machine
        self.dns = dns
        self.public_ip = public_ip
        self.private_ip = private_ip
        self.remote_provider = remote_provider
        self.remote_paras = remote_paras
        self.user_template = user_template
        self.create_time = create_time
        self.last_modify_time = last_modify_time

    def json(self):
        return to_json(self, self.__class__)

    def __repr__(self):
        return "VMConfig: " + self.json()

# ------------------------------ Tables are introduced by azure-auto-deploy ------------------------------
