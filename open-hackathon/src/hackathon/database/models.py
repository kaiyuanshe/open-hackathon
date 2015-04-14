# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#
# The MIT License (MIT)
#  
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#  
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#  
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import backref, relation
from . import Base, db_adapter
from datetime import datetime
import uuid
import json


def relationship(*arg, **kw):
    ret = relation(*arg, **kw)
    db_adapter.commit()
    return ret


def date_serializer(date):
    return long((date - datetime(1970, 1, 1)).total_seconds() * 1000)


def to_dic(inst, cls):
    # add your coversions for things like datetime's
    # and what-not that aren't serializable.
    convert = dict()
    convert[DateTime] = date_serializer

    # todo datatime
    d = dict()
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        if c.type.__class__ in convert.keys() and v is not None:
            try:
                func = convert[c.type.__class__]
                d[c.name] = func(v)
            except:
                d[c.name] = "Error:  Failed to covert using ", str(convert[c.type.__class__])
        # elif v is None:
        # d[c.name] = str()
        else:
            d[c.name] = v
    return d


def to_json(inst, cls):
    return json.dumps(to_dic(inst, cls))


class DBBase(Base):
    """
    DB model base class, providing basic functions
    """
    __abstract__ = True

    def __init__(self, **kwargs):
        super(DBBase, self).__init__(**kwargs)

    def dic(self):
        return to_dic(self, self.__class__)

    def json(self):
        return to_json(self, self.__class__)

    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__, self.json())


class User(DBBase):
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

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.get_user_id())

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()
        if self.last_login_time is None:
            self.last_login_time = datetime.utcnow()
        if self.slug is None:
            self.slug = str(uuid.uuid1())[0:8]  # todo generate a real slug


class UserEmail(DBBase):
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


class UserToken(DBBase):
    __tablename__ = 'user_token'

    id = Column(Integer, primary_key=True)
    token = Column(String(50), unique=True, nullable=False)

    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('User', backref=backref('tokens', lazy='dynamic'))

    issue_date = Column(DateTime)
    expire_date = Column(DateTime, nullable=False)

    def __init__(self, **kwargs):
        super(UserToken, self).__init__(**kwargs)
        if self.issue_date is None:
            self.issue_date = datetime.utcnow()


class Register(DBBase):
    __tablename__ = 'register'

    id = Column(Integer, primary_key=True)
    register_name = Column(String(80))
    email = Column(String(120), unique=True)
    create_time = Column(DateTime)
    description = Column(String(200))
    enabled = Column(Integer)  # 0: disabled 1:enabled

    phone = Column(String(11))
    sex = Column(Integer)   #0:women 1:man
    age = Column(Integer)
    career = Column(String(16))
    qq = Column(String(16))
    weibo = Column(String(32))
    wechat = Column(String(32))
    address = Column(String(80))
    status = Column(Integer)  # 0: havn't audit 1: audit passed 2:audit reject
    user_id = Column(Integer)

    hackathon_id = Column(Integer, ForeignKey('hackathon.id', ondelete='CASCADE'))
    hackathon = relationship('Hackathon', backref=backref('registers', lazy='dynamic'))

    def __init__(self, **kwargs):
        super(Register, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()
        if self.enabled is None:
            self.enabled = 1
        self.online = 0


class Hackathon(DBBase):
    __tablename__ = 'hackathon'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    sponsor = Column(Integer)
    status = Column(Integer)
    check_register = Column(Integer)  # 1=True 0=False

    start_time = Column(DateTime)
    end_time = Column(DateTime)
    create_time = Column(DateTime)
    update_time = Column(DateTime)

    registration_start_time = Column(DateTime)
    registration_end_time = Column(DateTime)
    description = Column(Text)


    def __init__(self, **kwargs):
        super(Hackathon, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()


class DockerHostServer(DBBase):
    __tablename__ = 'docker_host_server'

    id = Column(Integer, primary_key=True)
    vm_name = Column(String(100), nullable=False)
    public_dns = Column(String(50))
    public_ip = Column(String(50))
    public_docker_api_port = Column(Integer)
    private_ip = Column(String(50))
    private_docker_api_port = Column(Integer)
    container_count = Column(Integer, nullable=False)
    container_max_count = Column(Integer, nullable=False)
    hackathon_id = Column(Integer, ForeignKey('hackathon.id', ondelete='CASCADE'))
    hackathon = relationship('Hackathon', backref=backref('docker_host_servers', lazy='dynamic'))


class Experiment(DBBase):
    """
    Experiment is launched once template is used:
    1. user use template directly (user manage his own azure resources through template)
    2. hackathon use template directly (hackathon manage its own azure resources through template)
    3. user use template via hackathon (online)
    """
    __tablename__ = 'experiment'

    id = Column(Integer, primary_key=True)
    # EStatus in enum.py
    status = Column(Integer)
    create_time = Column(DateTime)
    last_heart_beat_time = Column(DateTime)
    template_id = Column(Integer, ForeignKey('template.id', ondelete='CASCADE'))
    template = relationship('Template', backref=backref('experiments', lazy='dynamic'))
    # negative if hackathon use template directly
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('User', backref=backref('experiments', lazy='dynamic'))
    # negative if user use template directly
    hackathon_id = Column(Integer, ForeignKey('hackathon.id', ondelete='CASCADE'))
    hackathon = relationship('Hackathon', backref=backref('experiments', lazy='dynamic'))

    def __init__(self, **kwargs):
        super(Experiment, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()
        if self.last_heart_beat_time is None:
            self.last_heart_beat_time = datetime.utcnow()


class VirtualEnvironment(DBBase):
    """
    Virtual environment is abstraction of smallest environment unit in template
    """
    __tablename__ = 'virtual_environment'

    id = Column(Integer, primary_key=True)
    # VEProvider in enum.py
    provider = Column(Integer)
    name = Column(String(100), nullable=False)
    image = Column(String(100))
    # VEStatus in enum.py
    status = Column(Integer)
    # VERemoteProvider in enum.py
    remote_provider = Column(Integer)
    remote_paras = Column(String(300))
    create_time = Column(DateTime)
    experiment_id = Column(Integer, ForeignKey('experiment.id', ondelete='CASCADE'))
    experiment = relationship('Experiment', backref=backref('virtual_environments', lazy='dynamic'))

    def __init__(self, **kwargs):
        super(VirtualEnvironment, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()


class DockerContainer(DBBase):
    """
    detail info of a VirtualEnvironment in case Docker
    """
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

    def __init__(self, exper, **kwargs):
        self.experiment = exper
        super(DockerContainer, self).__init__(**kwargs)
        self.status = 0
        if self.create_time is None:
            self.create_time = datetime.utcnow()


class PortBinding(DBBase):
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


class Announcement(DBBase):
    __tablename__ = 'announcement'

    id = Column(Integer, primary_key=True)
    content = Column(String(200))
    enabled = Column(Integer)  # 1=enabled 0=disabled
    create_time = Column(DateTime)

    def __init__(self, **kwargs):
        super(Announcement, self).__init__(**kwargs)
        if self.enabled is None:
            self.enabled = 1
        if self.create_time is None:
            self.create_time = datetime.utcnow()


class Template(DBBase):
    __tablename__ = 'template'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    url = Column(String(200))  # backup, templates' location
    provider = Column(Integer)
    create_time = Column(DateTime)
    description = Column(Text)
    virtual_environment_count = Column(Integer)

    hackathon_id = Column(Integer, ForeignKey('hackathon.id', ondelete='CASCADE'))
    hackathon = relationship('Hackathon', backref=backref('templates', lazy='dynamic'))

    def __init__(self, **kwargs):
        super(Template, self).__init__(**kwargs)
        if self.virtual_environment_count is None:
            self.virtual_environment_count = 0
        if self.create_time is None:
            self.create_time = datetime.utcnow()


# ------------------------------ Tables are introduced by azure formation ------------------------------


class AzureKey(DBBase):
    """
    Azure certificate information of user/hackathon
    """
    __tablename__ = 'azure_key'

    id = Column(Integer, primary_key=True)
    # cert file should be uploaded to azure portal
    cert_url = Column(String(200))
    # pem file should be saved in where this program run
    pem_url = Column(String(200))
    subscription_id = Column(String(100))
    management_host = Column(String(100))
    create_time = Column(DateTime)
    last_modify_time = Column(DateTime)

    def __init__(self, **kwargs):
        super(AzureKey, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()
        if self.last_modify_time is None:
            self.last_modify_time = datetime.utcnow()


class UserAzureKey(DBBase):
    __tablename__ = 'user_azure_key'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('User', backref=backref('user_azure_key_u', lazy='dynamic'))
    azure_key_id = Column(Integer, ForeignKey('azure_key.id', ondelete='CASCADE'))
    azure_key = relationship('AzureKey', backref=backref('user_azure_key_a', lazy='dynamic'))


class HackathonAzureKey(DBBase):
    __tablename__ = 'hackathon_azure_key'

    id = Column(Integer, primary_key=True)
    hackathon_id = Column(Integer, ForeignKey('hackathon.id', ondelete='CASCADE'))
    hackathon = relationship('Hackathon', backref=backref('hackathon_azure_key_h', lazy='dynamic'))
    azure_key_id = Column(Integer, ForeignKey('azure_key.id', ondelete='CASCADE'))
    azure_key = relationship('AzureKey', backref=backref('hackathon_azure_key_a', lazy='dynamic'))


class AzureLog(DBBase):
    """
    Azure operation log for every experiment
    """
    __tablename__ = 'azure_log'

    id = Column(Integer, primary_key=True)
    # ALOperation in enum.py
    operation = Column(String(50))
    # ALStatus in enum.py
    status = Column(String(50))
    # Note if no info and error
    note = Column(String(500))
    # None if no error
    code = Column(Integer)
    experiment_id = Column(Integer, ForeignKey('experiment.id', ondelete='CASCADE'))
    experiment = relationship('Experiment', backref=backref('azure_log', lazy='dynamic'))
    exec_time = Column(DateTime)

    def __init__(self, **kwargs):
        super(AzureLog, self).__init__(**kwargs)
        if self.exec_time is None:
            self.exec_time = datetime.utcnow()


class AzureStorageAccount(DBBase):
    """
    Azure storage account information
    """
    __tablename__ = 'azure_storage_account'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(String(100))
    label = Column(String(50))
    location = Column(String(50))
    # ASAStatus in enum.py
    status = Column(String(50))
    experiment_id = Column(Integer, ForeignKey('experiment.id', ondelete='CASCADE'))
    experiment = relationship('Experiment', backref=backref('azure_storage_account', lazy='dynamic'))
    create_time = Column(DateTime)
    last_modify_time = Column(DateTime)

    def __init__(self, **kwargs):
        super(AzureStorageAccount, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()
        if self.last_modify_time is None:
            self.last_modify_time = datetime.utcnow()


class AzureCloudService(DBBase):
    """
    Azure cloud service information
    """
    __tablename__ = 'azure_cloud_service'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    label = Column(String(50))
    location = Column(String(50))
    # ACSStatus in enum.py
    status = Column(String(50))
    experiment_id = Column(Integer, ForeignKey('experiment.id', ondelete='CASCADE'))
    experiment = relationship('Experiment', backref=backref('azure_cloud_service', lazy='dynamic'))
    create_time = Column(DateTime)
    last_modify_time = Column(DateTime)

    def __init__(self, **kwargs):
        super(AzureCloudService, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()
        if self.last_modify_time is None:
            self.last_modify_time = datetime.utcnow()


class AzureDeployment(DBBase):
    """
    Azure deployment information
    """
    __tablename__ = 'azure_deployment'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    slot = Column(String(50))
    # ADStatus in enum.py
    status = Column(String(50))
    cloud_service_id = Column(Integer, ForeignKey('azure_cloud_service.id', ondelete='CASCADE'))
    cloud_service = relationship('AzureCloudService', backref=backref('azure_deployment_c', lazy='dynamic'))
    experiment_id = Column(Integer, ForeignKey('experiment.id', ondelete='CASCADE'))
    experiment = relationship('Experiment', backref=backref('azure_deployment_e', lazy='dynamic'))
    create_time = Column(DateTime)
    last_modify_time = Column(DateTime)

    def __init__(self, **kwargs):
        super(AzureDeployment, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()
        if self.last_modify_time is None:
            self.last_modify_time = datetime.utcnow()


class AzureVirtualMachine(DBBase):
    """
    Azure virtual machine information
    """
    __tablename__ = 'azure_virtual_machine'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    label = Column(String(50))
    # AVMStatus in enum.py
    status = Column(String(50))
    dns = Column(String(50))
    public_ip = Column(String(50))
    private_ip = Column(String(50))
    deployment_id = Column(Integer, ForeignKey('azure_deployment.id', ondelete='CASCADE'))
    deployment = relationship('AzureDeployment', backref=backref('azure_virtual_machines_d', lazy='dynamic'))
    experiment_id = Column(Integer, ForeignKey('experiment.id', ondelete='CASCADE'))
    experiment = relationship('Experiment', backref=backref('azure_virtual_machines_e', lazy='dynamic'))
    virtual_environment_id = Column(Integer, ForeignKey('virtual_environment.id', ondelete='CASCADE'))
    virtual_environment = relationship('VirtualEnvironment',
                                       backref=backref('azure_virtual_machines_v', lazy='dynamic'))
    create_time = Column(DateTime)
    last_modify_time = Column(DateTime)

    def __init__(self, **kwargs):
        super(AzureVirtualMachine, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()
        if self.last_modify_time is None:
            self.last_modify_time = datetime.utcnow()


class AzureEndpoint(DBBase):
    """
    Input endpoint information of Azure virtual machine
    """
    __tablename__ = 'azure_endpoint'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    protocol = Column(String(50))
    public_port = Column(Integer)
    private_port = Column(Integer)
    virtual_machine_id = Column(Integer, ForeignKey('azure_virtual_machine.id', ondelete='CASCADE'))
    virtual_machine = relationship('AzureVirtualMachine', backref=backref('azure_endpoints', lazy='dynamic'))
    create_time = Column(DateTime)
    last_modify_time = Column(DateTime)

    def __init__(self, **kwargs):
        super(AzureEndpoint, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()
        if self.last_modify_time is None:
            self.last_modify_time = datetime.utcnow()


# ------------------------------ Tables for those logic around admin-site --------------------------------


class AdminUser(DBBase):
    __tablename__ = 'admin_user'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    nickname = Column(String(50))
    openid = Column(String(100))
    avatar_url = Column(String(200))
    access_token = Column(String(100))
    online = Column(Integer)  # 0:offline 1:online
    create_time = Column(DateTime)
    last_login_time = Column(DateTime)

    def __init__(self, **kwargs):
        super(AdminUser, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()
        if self.last_login_time is None:
            self.last_login_time = datetime.utcnow()


# if self.slug is None:
# self.slug = str(uuid.uuid1())[0:8]  # todo generate a real slug


class AdminEmail(DBBase):
    __tablename__ = 'admin_email'
    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    email = Column(String(120))
    primary_email = Column(Integer)  # 0:NOT Primary Email 1:Primary Email
    verified = Column(Integer)  # 0 for not verified, 1 for verified

    admin_id = Column(Integer, ForeignKey('admin_user.id', ondelete='CASCADE'))
    admin = relationship('AdminUser', backref=backref('emails', lazy='dynamic'))


class AdminToken(DBBase):
    __tablename__ = 'admin_token'
    id = Column(Integer, primary_key=True)
    token = Column(String(50), unique=True, nullable=False)

    admin_id = Column(Integer, ForeignKey('admin_user.id', ondelete='CASCADE'))
    admin = relationship('AdminUser', backref=backref('tokens', lazy='dynamic'))

    issue_date = Column(DateTime)
    expire_date = Column(DateTime, nullable=False)

    def __init__(self, **kwargs):
        super(AdminToken, self).__init__(**kwargs)
        if self.issue_date is None:
            self.issue_date = datetime.utcnow()


class AdminUserHackathonRel(DBBase):
    __tablename__ = 'admin_user_hackathon_rel'
    id = Column(Integer, primary_key=True)
    admin_email = Column(String(120))
    role_type = Column(Integer)
    hackathon_id = Column(Integer)
    state = Column(Integer)
    remarks = Column(String(255))
    create_time = Column(DateTime)

    def __init__(self, **kwargs):
        super(AdminUserHackathonRel, self).__init__(**kwargs)
        if self.create_time is None:
            self.create_time = datetime.utcnow()
