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

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, TypeDecorator
from sqlalchemy.orm import backref, relation
from . import Base, db_adapter
from datetime import datetime
from hackathon.util import get_now
import json
from pytz import utc
from dateutil import parser

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
    convert[TZDateTime] = date_serializer

    d = dict()
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        if c.type.__class__ in convert.keys() and v is not None:
            try:
                func = convert[c.type.__class__]
                d[c.name] = func(v)
            except:
                d[c.name] = "Error:  Failed to covert using ", str(convert[c.type.__class__])
        else:
            d[c.name] = v
    return d


def to_json(inst, cls):
    return json.dumps(to_dic(inst, cls))


class TZDateTime(TypeDecorator):
    '''
        usage: remove datetime's tzinfo
        To set all datetime datas are the naive datetime (tzinfo=None) in the whole environment
    '''

    impl = DateTime

    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, basestring) or isinstance(value, str):
                value = parser.parse(value)
            if isinstance(value, datetime):
                if value.tzinfo is not None:
                    value = value.astimezone(utc)
                    value.replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if isinstance(value, datetime):
                if value.tzinfo is not None:
                    value = value.astimezone(utc)
                    value.replace(tzinfo=None)
        return value


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
    password = Column(String(100))  # encrypted password for the default admin/guest users.
    name = Column(String(50))
    nickname = Column(String(50))
    provider = Column(String(20))
    openid = Column(String(100))
    avatar_url = Column(String(200))
    access_token = Column(String(100))
    online = Column(Integer)  # 0:offline 1:online
    create_time = Column(TZDateTime, default=get_now())
    last_login_time = Column(TZDateTime, default=get_now())

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


class UserEmail(DBBase):
    __tablename__ = 'user_email'

    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    email = Column(String(120))
    primary_email = Column(Integer)  # 0:NOT Primary Email 1:Primary Email
    verified = Column(Integer)  # 0 for not verified, 1 for verified
    create_time = Column(TZDateTime, default=get_now())
    update_time = Column(TZDateTime)

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

    issue_date = Column(TZDateTime, default=get_now())
    expire_date = Column(TZDateTime, nullable=False)

    def __init__(self, **kwargs):
        super(UserToken, self).__init__(**kwargs)


class UserHackathonRel(DBBase):
    __tablename__ = 'user_hackathon_rel'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    create_time = Column(TZDateTime, default=get_now())
    update_time = Column(TZDateTime)
    description = Column(String(200))
    status = Column(Integer)  # 0: havn't audit 1: audit passed 2:audit reject
    deleted = Column(Integer, default=0)  # 0:false  1-true
    git_project = Column(String(200))  # git project url

    user = relationship('User', backref=backref('registers', lazy='dynamic'))

    hackathon_id = Column(Integer, ForeignKey('hackathon.id', ondelete='CASCADE'))
    hackathon = relationship('Hackathon', backref=backref('registers', lazy='dynamic'))

    def __init__(self, **kwargs):
        super(UserHackathonRel, self).__init__(**kwargs)


class UserProfile(DBBase):
    __tablename__ = 'user_profile'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), unique=True)
    real_name = Column(String(80))
    phone = Column(String(20))
    gender = Column(Integer)  # 0:women 1:man
    age = Column(Integer)
    career_type = Column(String(50))
    career = Column(String(50))
    qq = Column(String(16))
    weibo = Column(String(32))
    wechat = Column(String(32))
    skype = Column(String(32))
    address = Column(String(100))

    user = relationship('User', backref=backref('profile', uselist=False))

    def __init__(self, **kwargs):
        super(UserProfile, self).__init__(**kwargs)


class UserTeamRel(DBBase):
    __tablename__ = 'user_team_rel'

    id = Column(Integer, primary_key=True)
    create_time = Column(TZDateTime, default=get_now())
    update_time = Column(TZDateTime)
    status = Column(Integer)  # 0:unaudit ,1:audit_passed, 2:audit_refused

    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('User', backref=backref('user_team_rels', lazy='dynamic'))

    team_id = Column(Integer, ForeignKey('team.id', ondelete='CASCADE'))
    team = relationship('Team', backref=backref('user_team_rels', lazy='dynamic'))

    def __init__(self, **kwargs):
        super(UserTeamRel, self).__init__(**kwargs)


class Team(DBBase):
    __tablename__ = 'team'

    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    display_name = Column(String(20))
    description = Column(Text)
    git_project = Column(String(200))
    logo = Column(String(200))
    create_time = Column(TZDateTime, default=get_now())
    update_time = Column(TZDateTime)

    leader_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    leader = relationship('User', backref=backref('lead_teams', lazy='dynamic'))

    hackathon_id = Column(Integer, ForeignKey('hackathon.id', ondelete='CASCADE'))
    hackathon = relationship('Hackathon', backref=backref('teams', lazy='dynamic'))

    def __init__(self, **kwargs):
        super(Team, self).__init__(**kwargs)


class Hackathon(DBBase):
    __tablename__ = 'hackathon'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(64))
    description = Column(Text)
    status = Column(Integer, default=0)  # 0-new 1-online 2-offline
    creator_id = Column(Integer, default=-1)
    type = Column(Integer, default=1)  # enum.HACK_TYPE

    event_start_time = Column(TZDateTime)
    event_end_time = Column(TZDateTime)
    registration_start_time = Column(TZDateTime)
    registration_end_time = Column(TZDateTime)
    judge_start_time = Column(TZDateTime)
    judge_end_time = Column(TZDateTime)

    basic_info = Column(Text)
    extra_info = Column(Text)

    create_time = Column(TZDateTime, default=get_now())
    update_time = Column(TZDateTime)
    archive_time = Column(TZDateTime)

    def dic(self):
        d = to_dic(self, self.__class__)
        d["basic_info"] = json.loads(self.basic_info or "{}")

        d["extra_info"] = json.loads(self.extra_info or "{}")
        return d

    def __init__(self, **kwargs):
        super(Hackathon, self).__init__(**kwargs)


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
    create_time = Column(TZDateTime, default=get_now())
    update_time = Column(TZDateTime)

    hackathon_id = Column(Integer, ForeignKey('hackathon.id', ondelete='CASCADE'))
    hackathon = relationship('Hackathon', backref=backref('docker_host_servers', lazy='dynamic'))

    def __init__(self, **kwargs):
        super(DockerHostServer, self).__init__(**kwargs)


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
    create_time = Column(TZDateTime, default=get_now())
    update_time = Column(TZDateTime)
    last_heart_beat_time = Column(TZDateTime, default=get_now())

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
    create_time = Column(TZDateTime, default=get_now())
    update_time = Column(TZDateTime)

    experiment_id = Column(Integer, ForeignKey('experiment.id', ondelete='CASCADE'))
    experiment = relationship('Experiment', backref=backref('virtual_environments', lazy='dynamic'))

    def __init__(self, **kwargs):
        super(VirtualEnvironment, self).__init__(**kwargs)


class DockerContainer(DBBase):
    """
    detail info of a VirtualEnvironment in case Docker
    """
    __tablename__ = 'docker_container'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    image = Column(String(50), nullable=False)
    container_id = Column(String(100))
    create_time = Column(TZDateTime, default=get_now())
    update_time = Column(TZDateTime)

    virtual_environment_id = Column(Integer, ForeignKey('virtual_environment.id', ondelete='CASCADE'))
    virtual_environment = relationship(VirtualEnvironment,
                                       backref=backref('container', uselist=False))

    host_server_id = Column(Integer)

    def __init__(self, expr, **kwargs):
        self.experiment = expr
        super(DockerContainer, self).__init__(**kwargs)


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

    url = Column(String(200))  # public url schema for display


class Announcement(DBBase):
    __tablename__ = 'announcement'

    id = Column(Integer, primary_key=True)
    content = Column(String(200))
    enabled = Column(Integer, default=1)  # 1=enabled 0=disabled
    create_time = Column(TZDateTime, default=get_now())
    update_time = Column(TZDateTime)

    def __init__(self, **kwargs):
        super(Announcement, self).__init__(**kwargs)


class Template(DBBase):
    __tablename__ = 'template'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    url = Column(String(200))
    azure_url = Column(String(200))
    provider = Column(Integer, default=0)
    creator_id = Column(Integer)
    status = Column(Integer)    # 1=online , 0=offline
    create_time = Column(TZDateTime, default=get_now())
    update_time = Column(TZDateTime)
    description = Column(Text)
    virtual_environment_count = Column(Integer, default=0)

    def __init__(self, **kwargs):
        super(Template, self).__init__(**kwargs)


class HackathonTemplateRel(DBBase):
    __tablename__ = 'hackathon_template_rel'

    id = Column(Integer, primary_key=True)
    create_time = Column(TZDateTime, default=get_now())
    update_time = Column(TZDateTime)
    team_id = Column(Integer)  # none: relations for all teams

    hackathon_id = Column(Integer, ForeignKey('hackathon.id', ondelete='CASCADE'))
    hackathon = relationship('Hackathon', backref=backref('hackathon_template_rels', lazy='dynamic'))

    template_id = Column(Integer, ForeignKey('template.id', ondelete='CASCADE'))
    template = relationship('Template', backref=backref('hackathon_template_rels', lazy='dynamic'))

    def __init__(self, **kwargs):
        super(HackathonTemplateRel, self).__init__(**kwargs)


# ------------------------------ Tables are introduced by azure formation ------------------------------

class AzureKey(DBBase):
    """
    Azure certificate information of user/hackathon
    """
    __tablename__ = 'azure_key'

    id = Column(Integer, primary_key=True)
    # cert_url is cert file path in azure
    cert_url = Column(String(200))
    # pem_url is pem file path in local
    pem_url = Column(String(200))
    subscription_id = Column(String(100))
    management_host = Column(String(100))
    create_time = Column(TZDateTime, default=get_now())
    last_modify_time = Column(TZDateTime, default=get_now())

    def __init__(self, **kwargs):
        super(AzureKey, self).__init__(**kwargs)


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
    exec_time = Column(TZDateTime, default=get_now())

    def __init__(self, **kwargs):
        super(AzureLog, self).__init__(**kwargs)


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
    create_time = Column(TZDateTime, default=get_now())
    last_modify_time = Column(TZDateTime, default=get_now())

    def __init__(self, **kwargs):
        super(AzureStorageAccount, self).__init__(**kwargs)


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
    create_time = Column(TZDateTime, default=get_now())
    last_modify_time = Column(TZDateTime, default=get_now())

    def __init__(self, **kwargs):
        super(AzureCloudService, self).__init__(**kwargs)


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
    create_time = Column(TZDateTime, default=get_now())
    last_modify_time = Column(TZDateTime, default=get_now())

    def __init__(self, **kwargs):
        super(AzureDeployment, self).__init__(**kwargs)


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
    create_time = Column(TZDateTime, default=get_now())
    last_modify_time = Column(TZDateTime, default=get_now())

    def __init__(self, **kwargs):
        super(AzureVirtualMachine, self).__init__(**kwargs)


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
    create_time = Column(TZDateTime, default=get_now())
    last_modify_time = Column(TZDateTime, default=get_now())

    def __init__(self, **kwargs):
        super(AzureEndpoint, self).__init__(**kwargs)


class AdminHackathonRel(DBBase):
    __tablename__ = 'admin_hackathon_rel'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('User', backref=backref('admin_hackathon_rels', lazy='dynamic'))

    role_type = Column(Integer)  # enum.ADMIN_ROLE_TYPE
    hackathon_id = Column(Integer)
    status = Column(Integer)  # enum.AdminHackathonRelStatus
    remarks = Column(String(255))
    create_time = Column(TZDateTime, default=get_now())
    update_time = Column(TZDateTime)

    def __init__(self, **kwargs):
        super(AdminHackathonRel, self).__init__(**kwargs)
