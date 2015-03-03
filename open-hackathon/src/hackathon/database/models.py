import sys
import email
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from . import Base
from . import UserMixin
from datetime import datetime
import uuid
import json


def to_json(inst, cls):
    # add your coversions for things like datetime's
    # and what-not that aren't serializable.
    convert = dict()
    convert[DateTime] = long

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


class User(UserMixin, Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    nickname = Column(String(50))
    openid = Column(String(100))
    avatar_url = Column(String(200))
    slug = Column(String(50), unique=True, nullable=False)  # can be used for branch name of github
    access_token = Column(String(100))
    online = Column(Integer)  # 0:offline 1:online
    create_time = Column(DateTime)
    last_login_time = Column(DateTime)

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


class UserEmail(Base):
    __tablename__ = 'user_email'

    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    email = Column(String(120))
    primary_email = Column(Integer)  # 0:NOT Primary Email 1:Primary Email
    verified = Column(Integer)  # 0 for not verified, 1 for verified

    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('User', backref=backref('emails', lazy='dynamic'))

    def get_user_email(self):
        return self.email

    def __init__(self, **kwargs):
        super(UserEmail, self).__init__(**kwargs)


class UserToken(Base):
    __tablename__ = 'user_token'

    id = Column(Integer, primary_key=True)
    token = Column(String(50), unique=True, nullable=False)

    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('User', backref=backref('tokens', lazy='dynamic'))

    issue_date = Column(DateTime)
    expire_date = Column(DateTime, nullable=False)

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


class Register(Base):
    __tablename__ = 'register'

    id = Column(Integer, primary_key=True)
    register_name = Column(String(80))
    email = Column(String(120), unique=True)
    create_time = Column(DateTime)
    description = Column(String(200))
    enabled = Column(Integer)  # 0: disabled 1:enabled
    jstrom_api = Column(String(50))
    jstrom_mgmt_portal = Column(String(50))

    hackathon_id = Column(Integer, ForeignKey('hackathon.id', ondelete='CASCADE'))
    hackathon = relationship('Hackathon', backref=backref('registers', lazy='dynamic'))

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


class Hackathon(Base):
    __tablename__ = 'hackathon'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    sponsor = Column(Integer)
    status = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    create_time = Column(DateTime)

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(Hackathon, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()

    def __repr__(self):
        return "Hackathon: " + self.json()


class DockerHostServer(Base):
    __tablename__ = 'docker_host_server'

    id = Column(Integer, primary_key=True)
    vm_name = Column(String(100), unique=True, nullable=False)
    public_dns = Column(String(50))
    public_docker_api_port = Column(Integer)
    private_ip = Column(String(50), unique=True)
    private_docker_api_port = Column(Integer)
    container_count = Column(Integer, nullable=False)
    container_max_count = Column(Integer, nullable=False)

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(DockerHostServer, self).__init__(**kwargs)

    def __repr__(self):
        return "HostServer: " + self.json()


class Experiment(Base):
    __tablename__ = 'experiment'

    id = Column(Integer, primary_key=True)
    status = Column(Integer)  # see enum.py
    create_time = Column(DateTime)
    last_heart_beat_time = Column(DateTime)

    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('User', backref=backref('experiments', lazy='dynamic'))

    hackathon_id = Column(Integer, ForeignKey('hackathon.id', ondelete='CASCADE'))
    hackathon = relationship('Hackathon', backref=backref('experiments', lazy='dynamic'))

    # adaptor for auto azure deploy
    user_template_id = Column(Integer, ForeignKey('user_template.id', ondelete='CASCADE'))
    user_template = relationship('UserTemplate', backref=backref('experiments', lazy='dynamic'))

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


class VirtualEnvironment(Base):
    __tablename__ = 'virtual_environment'

    id = Column(Integer, primary_key=True)
    provider = Column(String(10), nullable=False)
    name = Column(String(100), nullable=False)
    image = Column(String(100))
    status = Column(Integer)  # see enum.py
    remote_provider = Column(String(20))
    remote_paras = Column(String(300))
    create_time = Column(DateTime)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', backref=backref('virtual_environments', lazy='dynamic'))

    experiment_id = Column(Integer, ForeignKey('experiment.id', ondelete='CASCADE'))
    experiment = relationship('Experiment', backref=backref('virtual_environments', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(VirtualEnvironment, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()

    def __repr__(self):
        return "VirtualEnvironment: " + self.json()


# detail info of a VirtualEnvironment in case Docker
class DockerContainer(Base):
    __tablename__ = 'docker_container'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    image = Column(String(50), nullable=False)
    container_id = Column(String(100))
    create_time = Column(DateTime)

    virtual_environment_id = Column(Integer, ForeignKey('virtual_environment.id', ondelete='CASCADE'))
    virtual_environment = relationship(VirtualEnvironment,
                                       backref=backref('container', uselist=False))

    host_server_id = Column(Integer, ForeignKey('docker_host_server.id', ondelete='CASCADE'))
    host_server = relationship('DockerHostServer', backref=backref('containers', lazy='dynamic'))

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


class PortBinding(Base):
    __tablename__ = 'port_binding'

    # for simplicity, the port won't be released until the corresponding container removed(not stopped).
    # that means a port occupied by stopped container won't be allocated to new container. So it's possible to start the
    # container again. And the number of port should be enough since we won't have too many containers on the same VM.
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    port_from = Column(Integer, nullable=False)
    port_to = Column(Integer, nullable=False)
    binding_type = Column(Integer)  # CloudService or Docker, see enum.py
    binding_resource_id = Column(
        Integer)  # DockerHostServer.id if binding_type is Docker, VM resource id if cloudservice

    virtual_environment_id = Column(Integer, ForeignKey('virtual_environment.id', ondelete='CASCADE'))
    virtual_environment = relationship('VirtualEnvironment', backref=backref('port_bindings', lazy='dynamic'))

    experiment_id = Column(Integer, ForeignKey('experiment.id', ondelete='CASCADE'))
    experiment = relationship('Experiment', backref=backref('port_bindings', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, **kwargs):
        super(PortBinding, self).__init__(**kwargs)

    def __repr__(self):
        return "PortBinding: " + self.json()


class Announcement(Base):
    __tablename__ = 'announcement'

    id = Column(Integer, primary_key=True)
    content = Column(String(200))
    enabled = Column(Integer)  # 1=enabled 0=disabled
    create_time = Column(DateTime)

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, content):
        self.content = content
        self.enabled = 1
        self.create_time = datetime.utcnow()

    def __repr__(self):
        return "Announcement: " + self.json()


class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    create_time = Column(DateTime)

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, name):
        self.name = name
        self.create_time = datetime.utcnow()

    def __repr__(self):
        return "Role: " + self.json()


class UserRole(Base):
    __tablename__ = 'user_role'

    id = Column(Integer, primary_key=True)
    create_time = Column(DateTime)

    user_id = Column(Integer(), ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('User', backref=backref('roles', lazy='dynamic'))

    role_id = Column(Integer(), ForeignKey('role.id', ondelete='CASCADE'))
    role = relationship('Role', backref=backref('users', lazy='dynamic'))

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, role, user):
        self.role = role
        self.user = user
        self.create_time = datetime.utcnow()

    def __repr__(self):
        return "UserRole: " + self.json()


class Template(Base):
    __tablename__ = 'template'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    url = Column(String(200))  # backup, templates' location
    provider = Column(String(20))
    create_time = Column(DateTime)

    hackathon_id = Column(Integer, ForeignKey('hackathon.id', ondelete='CASCADE'))
    hackathon = relationship('Hackathon', backref=backref('templates', lazy='dynamic'))

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


class UserTemplate(Base):
    __tablename__ = 'user_template'

    id = Column(Integer, primary_key=True)
    create_time = Column(DateTime)
    last_modify_time = Column(DateTime)
    user_id = Column(Integer(), ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('User', backref=backref('user_template', lazy='dynamic'))
    template_id = Column(Integer, ForeignKey('template.id', ondelete='CASCADE'))
    template = relationship('Template', backref=backref('user_template', lazy='dynamic'))

    def __init__(self, user, template, create_time=None, last_modify_time=None):
        if create_time is None:
            create_time = datetime.utcnow()
        if last_modify_time is None:
            last_modify_time = datetime.utcnow()
        self.user = user
        self.template = template
        self.create_time = create_time
        self.last_modify_time = last_modify_time


class UserOperation(Base):
    __tablename__ = 'user_operation'

    id = Column(Integer, primary_key=True)
    operation = Column(String(50))
    status = Column(String(50))
    note = Column(String(500))
    exec_time = Column(DateTime)
    user_template_id = Column(Integer, ForeignKey('user_template.id', ondelete='CASCADE'))
    user_template = relationship('UserTemplate', backref=backref('user_operation', lazy='dynamic'))

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


class UserResource(Base):
    __tablename__ = 'user_resource'

    id = Column(Integer, primary_key=True)
    type = Column(String(50))
    name = Column(String(50))
    status = Column(String(50))
    create_time = Column(DateTime)
    last_modify_time = Column(DateTime)
    user_template_id = Column(Integer, ForeignKey('user_template.id', ondelete='CASCADE'))
    user_template = relationship('UserTemplate', backref=backref('user_resource1', lazy='dynamic'))
    # for deployment and virtual machine
    cloud_service_id = Column(Integer, ForeignKey('user_resource.id', ondelete='CASCADE'))

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


class VMEndpoint(Base):
    __tablename__ = 'vm_endpoint'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    protocol = Column(String(50))
    public_port = Column(Integer)
    private_port = Column(Integer)
    create_time = Column(DateTime)
    last_modify_time = Column(DateTime)
    cloud_service_id = Column(Integer, ForeignKey('user_resource.id', ondelete='CASCADE'))
    cloud_service = relationship('UserResource', foreign_keys=[cloud_service_id],
                                 backref=backref('vm_endpoint1', lazy='dynamic'))
    virtual_machine_id = Column(Integer, ForeignKey('user_resource.id', ondelete='CASCADE'))
    virtual_machine = relationship('UserResource', foreign_keys=[virtual_machine_id],
                                   backref=backref('vm_endpoint2', lazy='dynamic'))

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


class VMConfig(Base):
    __tablename__ = 'vm_config'

    id = Column(Integer, primary_key=True)
    dns = Column(String(50))
    public_ip = Column(String(50))
    private_ip = Column(String(50))
    create_time = Column(DateTime)
    last_modify_time = Column(DateTime)
    virtual_machine_id = Column(Integer, ForeignKey('user_resource.id', ondelete='CASCADE'))
    virtual_machine = relationship('UserResource', backref=backref('vm_config1', lazy='dynamic'))
    remote_provider = Column(String(20))
    remote_paras = Column(String(300))
    user_template_id = Column(Integer, ForeignKey('user_template.id', ondelete='CASCADE'))
    user_template = relationship('UserTemplate', backref=backref('vm_config2', lazy='dynamic'))

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

# ------------------------------ Tables for those logic around admin-site --------------------------------
class AdminToken(Base):
    id = Column(Integer, primary_key=True)
    token = Column(String(50), unique=True, nullable=False)

    admin_id = Column(Integer, ForeignKey('admin_user.id', ondelete='CASCADE'))
    admin = relationship('AdminUser', backref=backref('tokens', lazy='dynamic'))

    issue_date = Column(DateTime)
    expire_date = Column(DateTime, nullable=False)

    def json(self):
        return to_json(self, self.__class__)

    def __init__(self, token, admin, expire_date, issue_date=None):
        if issue_date is None:
            issue_date = datetime.utcnow()

        self.token = token
        self.admin = admin
        self.expire_date = expire_date
        self.issue_date = issue_date

    def __repr__(self):
        return "AdminToken: " + self.json()


# ------------------------------ Tables for those logic around admin-site --------------------------------
