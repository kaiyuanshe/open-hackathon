# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import hashlib
from mongoengine import QuerySet, DateTimeField, DynamicDocument, EmbeddedDocument, StringField, \
    BooleanField, IntField, DynamicEmbeddedDocument, EmbeddedDocumentListField, URLField, ListField, \
    EmbeddedDocumentField, ReferenceField, UUIDField, DictField, DynamicField, PULL

from hackathon.util import get_now, make_serializable
from hackathon.constants import TEMPLATE_STATUS, HACK_USER_TYPE
from hackathon.hmongo.pagination import Pagination
from hackathon import app


# from werkzeug.security import generate_password_hash, check_password_hash

def to_dic(obj):
    ret = make_serializable(obj.to_mongo().to_dict())

    # normalize
    if "_id" in ret:
        ret["id"] = ret.pop("_id")

    if "_cls" in ret:
        ret.pop("_cls")

    return ret


class HQuerySet(QuerySet):
    """add some handy helpers on the default query set from mongoengine
    """

    def paginate(self, page, per_page):
        return Pagination(self, page, per_page)


class HDocumentBase(DynamicDocument):
    """
    DB model base class, providing basic functions
    """

    create_time = DateTimeField(default=get_now())
    update_time = DateTimeField(default=get_now())

    meta = {
        'allow_inheritance': True,
        'abstract': True,
        'queryset_class': HQuerySet}
    unsafe_columns = []

    def __init__(self, **kwargs):
        super(HDocumentBase, self).__init__(**kwargs)

    def dic(self):
        result = to_dic(self)
        for k in self.unsafe_columns:
            result.pop(k, None)
        return result

    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__, self.to_json())


class UserEmail(EmbeddedDocument):
    email = StringField()
    primary_email = BooleanField()
    verified = BooleanField()


class UserProfile(DynamicEmbeddedDocument):
    address = StringField()
    age = IntField(min_value=1)
    career = StringField()
    career_type = StringField()
    gender = IntField()  # 0:women 1:man
    notes = StringField()  # a short activity or mood
    phone = StringField(max_length=20)
    qq = StringField()
    real_name = StringField(max_length=80)
    self_introduction = StringField()
    skype = StringField()
    wechat = StringField()
    weibo = StringField()
    avatar_url = URLField()  # high priority than avatar_url in User


class User(HDocumentBase):
    name = StringField(max_length=50, min_length=1, required=True)
    nickname = StringField(max_length=50, min_length=1, required=True)
    password = StringField(max_length=100)
    emails = EmbeddedDocumentListField(UserEmail)
    is_super = BooleanField(default=False)
    profile = EmbeddedDocumentField(UserProfile)
    provider = StringField(max_length=20)
    openid = StringField(max_length=100)
    avatar_url = StringField()  # if avatar_url in UserProfile setted, this is not used
    access_token = StringField(max_length=1024)
    online = BooleanField(default=False)
    last_login_time = DateTimeField()
    login_times = IntField(default=1)  # a new user usually added upon whose first login, by default 1 thus

    unsafe_columns = ["password"]

    meta = {
        "indexes": [
            {
                # default unqiue is not sparse, so we have to set it by ourselves
                "fields": ["provider", "openid"],
                "unique": True,
                "sparse": True}]}

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    @staticmethod
    def get_encode_password(pwd):
        m = hashlib.md5()
        pwd = pwd + app.config['SECRET_KEY']
        m.update(pwd.encode())
        return m.hexdigest()

    def set_password(self, pwd):
        self.password = self.get_encode_password(pwd)

    def check_password(self, pwd):
        return self.get_encode_password(pwd) == self.password


class UserToken(HDocumentBase):
    token = UUIDField(required=True)
    user = ReferenceField(User)
    issue_date = DateTimeField(default=get_now())
    expire_date = DateTimeField(required=True)

    meta = {
        'indexes': [
            {
                # See mongodb and mongo engine documentation for details
                # by default, mongoengine will add a `_cls` field with the index as a compund index
                # but mongodb only support Single Key Index on Hashed Token so far
                # set the `cls` option to False can disable this beahviour on mongoengine
                "fields": ["#token"],
                "cls": False}]}

    def __init__(self, **kwargs):
        super(UserToken, self).__init__(**kwargs)


class K8sCluster(DynamicEmbeddedDocument):
    api_url = StringField(required=True)
    token = StringField(required=True)
    namespace = StringField(default="default")
    gateway = ListField()
    creator = ReferenceField(User)


class NetworkConfigTemplate(HDocumentBase):
    """ Network config for generate K8s yml"""

    name = StringField(required=True, unique=True)
    protocol = StringField()
    port = IntField(max_value=65535)


class Template(HDocumentBase):
    name = StringField(required=True, unique=True)
    provider = IntField()
    status = IntField(default=TEMPLATE_STATUS.UNCHECKED)  # constants.TEMPLATE_STATUS
    description = StringField()

    # todo delete K8s cluster info: Templates should be more generic and cluster unrelated
    k8s_cluster = EmbeddedDocumentField(K8sCluster)

    # K8s yml template
    content = StringField()  # template content
    template_args = DictField()

    # Docker image template
    docker_image = StringField()
    network_configs = ListField(NetworkConfigTemplate)

    virtual_environment_count = IntField(min_value=0, required=True)
    creator = ReferenceField(User)

    def __init__(self, **kwargs):
        super(Template, self).__init__(**kwargs)


class Organization(DynamicEmbeddedDocument):
    id = UUIDField(required=True)
    name = StringField(required=True)
    description = StringField()
    homepage = URLField()
    logo = URLField()
    organization_type = IntField()  # see ORGANIZATION_TYPE : ORGANIZER = 1, PARTNER = 2


class Award(EmbeddedDocument):
    id = UUIDField(required=True)
    name = StringField(required=True)
    sub_name = StringField()
    description = StringField(required=True)
    level = IntField(min_value=0, max_value=10)  # 0-10
    quota = IntField(min_value=1, default=1, required=True)
    award_url = StringField()


class AzureKey(HDocumentBase):
    """
    Azure certificate information of user/hackathon
    Open-hackathon will try to use local certification file, if it doesn't exist, open-hackathon will try to
    recover it from azure.abs    """
    cert_url = StringField(required=True)  # cert_url is cert file path in azure
    # pem_url is "encrypted" pem file path in azure, so be careful to use this,
    # at the most time you should use get_local_pem_url()
    pem_url = StringField(required=True)
    subscription_id = StringField(required=True)
    management_host = StringField(required=True)
    verified = BooleanField()

    def __init__(self, **kwargs):
        super(AzureKey, self).__init__(**kwargs)


class Hackathon(HDocumentBase):
    name = StringField(unique=True, required=True)
    display_name = StringField(required=True)
    ribbon = StringField()  # a short sentence of advertisement
    short_description = StringField()
    location = StringField()
    description = StringField()
    banners = ListField()
    status = IntField(default=0)  # 0-new 1-online 2-offline 3-apply-online
    creator = ReferenceField(User)
    config = DictField()  # max_enrollment, auto_approve, login_provider
    type = IntField(default=1)  # enum.HACK_TYPE
    organizers = EmbeddedDocumentListField(Organization)
    tags = ListField()
    awards = EmbeddedDocumentListField(Award)
    templates = ListField(ReferenceField(Template, reverse_delete_rule=PULL))  # templates for hackathon
    azure_keys = ListField(ReferenceField(AzureKey))

    event_start_time = DateTimeField()
    event_end_time = DateTimeField()
    registration_start_time = DateTimeField()
    registration_end_time = DateTimeField()
    judge_start_time = DateTimeField()
    judge_end_time = DateTimeField()
    archive_time = DateTimeField()

    def __init__(self, **kwargs):
        super(Hackathon, self).__init__(**kwargs)


class UserHackathon(HDocumentBase):
    user = ReferenceField(User)
    hackathon = ReferenceField(Hackathon)
    role = IntField(default=HACK_USER_TYPE.COMPETITOR)  # 0-visitor 1-admin 2-judge 3-competitor
    status = IntField()  # 0-not approved user 1-approved user 2-refused user 3-auto approved user
    like = BooleanField(default=True)
    assets = DictField(default={})  # assets for user
    remark = StringField()
    deleted = BooleanField(default=False)

    def __init__(self, **kwargs):
        super(UserHackathon, self).__init__(**kwargs)


class HackathonStat(HDocumentBase):
    type = StringField()  # class HACKATHON_STAT
    count = IntField(min_value=0)
    hackathon = ReferenceField(Hackathon)


class HackathonNotice(HDocumentBase):
    category = IntField()  # category: Class HACK_NOTICE_CATEGORY, controls how icons/descriptions are shown at front-end
    event = IntField()  # event: Class HACK_NOTICE_EVENT, records the specfic event that triggers current notice
    content = StringField()
    related_id = DynamicField()
    link = StringField()
    creator = ReferenceField(User)
    hackathon = ReferenceField(Hackathon)
    receiver = ReferenceField(User)
    is_read = BooleanField(default=False)

    def __init__(self, **kwargs):
        super(HackathonNotice, self).__init__(**kwargs)


class TeamWork(EmbeddedDocument):
    id = UUIDField(required=True)
    description = StringField()
    type = IntField(required=True)  # see TEAM_SHOW_TYPE
    uri = StringField()
    create_time = DateTimeField(default=get_now())


class TeamScore(EmbeddedDocument):
    type = IntField(default=0)
    score = IntField(required=True, min_value=0)
    reason = StringField()
    score_date = DateTimeField(default=get_now())
    judge = ReferenceField(User)


class TeamMember(EmbeddedDocument):
    join_time = DateTimeField()
    status = IntField()  # 0:unaudit ,1:audit_passed, 2:audit_refused
    user = ReferenceField(User)


class Team(HDocumentBase):
    name = StringField(required=True)
    description = StringField()
    logo = StringField()
    leader = ReferenceField(User)
    cover = StringField()
    project_name = StringField()
    project_description = StringField()
    dev_plan = StringField()
    hackathon = ReferenceField(Hackathon)
    works = EmbeddedDocumentListField(TeamWork)
    scores = EmbeddedDocumentListField(TeamScore)
    members = EmbeddedDocumentListField(TeamMember)
    awards = ListField()  # list of uuid. UUID reference class Award-id
    assets = DictField()  # assets for team
    azure_keys = ListField(ReferenceField(AzureKey))
    templates = ListField(ReferenceField(Template))  # templates for team

    def __init__(self, **kwargs):
        super(Team, self).__init__(**kwargs)


class DockerHostServer(HDocumentBase):
    vm_name = StringField(required=True)
    public_dns = StringField()
    public_ip = StringField()
    public_docker_api_port = IntField(min_value=1, max_value=65535, default=4243)
    private_ip = StringField()
    private_docker_api_port = IntField(min_value=1, max_value=65535, default=4243)
    container_count = IntField(required=True, min_value=0, default=0)
    container_max_count = IntField(required=True, min_value=0)
    is_auto = BooleanField(default=False)  # 0-started manually 1-started by OHP server
    state = IntField(default=0)  # 0-VM starting, 1-docker init, 2-docker API ready, 3-unavailable
    disabled = BooleanField(default=False)  # T-disabled by manager, F-available
    hackathon = ReferenceField(Hackathon)

    def __init__(self, **kwargs):
        super(DockerHostServer, self).__init__(**kwargs)


class PortBinding(DynamicEmbeddedDocument):
    # for simplicity, the port won't be released until the corresponding container removed(not stopped).
    # that means a port occupied by stopped container won't be allocated to new container. So it's possible to start the
    # container again. And the number of port should be enough since we won't have too many containers on the same VM.
    name = StringField()
    is_public = BooleanField()
    public_port = IntField()  # port that are public accessible
    host_port = IntField()  # port on hosted VM
    container_port = IntField()  # port inside docker container
    url = StringField()  # public url pattern for display where host and port should be replaced


class DockerContainer(DynamicEmbeddedDocument):
    name = StringField(required=True, unique=True)
    image = StringField()
    container_id = StringField()
    host_server = ReferenceField(DockerHostServer)
    port_bindings = EmbeddedDocumentListField(PortBinding, default=[])


class AzureStorageAccount(DynamicEmbeddedDocument):
    name = StringField(required=True)
    description = StringField()
    label = StringField()
    location = StringField(required=True)
    # ASAStatus in enum.py
    status = StringField()
    create_time = DateTimeField()
    update_time = DateTimeField()
    deletable = BooleanField()  # F-cannot delete T-can be deleted


class AzureCloudService(DynamicEmbeddedDocument):
    name = StringField()
    label = StringField()
    location = StringField()
    # ACSStatus in enum.py
    status = StringField()
    azure_key = ReferenceField(AzureKey)
    deletable = BooleanField()  # F-cannot delete T-can be deleted


class AzureDeployment(DynamicEmbeddedDocument):
    name = StringField()
    slot = StringField()
    # ADStatus in enum.py
    status = StringField()
    cloud_service = EmbeddedDocumentField(AzureCloudService)
    create_time = DateTimeField()
    update_time = DateTimeField()
    deletable = BooleanField()  # F-cannot delete T-can be deleted


class AzureEndPoint(DynamicEmbeddedDocument):
    name = StringField()
    protocol = StringField()
    public_port = IntField()
    private_port = IntField()
    url = StringField()


class AzureVirtualMachine(DynamicEmbeddedDocument):
    name = StringField(required=True)
    label = StringField()
    # AVMStatus in enum.py
    dns = StringField()
    public_ip = StringField()
    private_ip = StringField()
    deployment = EmbeddedDocumentField(AzureDeployment)
    create_time = DateTimeField()
    update_time = DateTimeField()
    deletable = BooleanField()  # F-cannot delete T-can be deleted
    end_points = EmbeddedDocumentListField(AzureEndPoint, default=[])


class K8sEnvironment(DynamicEmbeddedDocument):
    # define k8s resource
    name = StringField(required=True)
    deployments = ListField()
    persistent_volume_claims = ListField()
    services = ListField()
    stateful_sets = ListField()


class VirtualEnvironment(DynamicEmbeddedDocument):
    """
    Virtual environment is abstraction of smallest environment unit in template
    """
    provider = IntField()  # VE_PROVIDER in enum.py
    name = StringField(required=True, unique=True)
    status = IntField(required=True)  # VEStatus in enum.py
    remote_provider = IntField()  # VERemoteProvider in enum.py
    remote_paras = DictField()
    create_time = DateTimeField(default=get_now())
    update_time = DateTimeField()
    docker_container = EmbeddedDocumentField(DockerContainer)
    azure_resource = EmbeddedDocumentField(AzureVirtualMachine)
    k8s_resource = EmbeddedDocumentField(K8sEnvironment)


class Experiment(HDocumentBase):
    status = IntField()  # EStatus in enum.py
    last_heart_beat_time = DateTimeField()
    template = ReferenceField(Template)
    user = ReferenceField(User)
    hackathon = ReferenceField(Hackathon)
    virtual_environments = EmbeddedDocumentListField(VirtualEnvironment, default=[])

    def __init__(self, **kwargs):
        super(Experiment, self).__init__(**kwargs)
