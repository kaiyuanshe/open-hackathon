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


class HTTP_HEADER:
    """Http header that hackathon server api requires

    Attributes:
        TOKEN: token for current login user to access the hackathon server APIs with @token_required
        HACKATHON_NAME: the name of hackathon related to the API call
    """
    TOKEN = "token"
    HACKATHON_NAME = "hackathon_name"


class OAUTH_PROVIDER:
    """Social Login that open-hackathon platform support"""
    GITHUB = "github"
    QQ = "qq"
    GITCAFE = "gitcafe"
    WEIBO = "weibo"
    LIVE = "live"
    ALAUDA = "alauda"


class HEALTH_STATUS:
    """The running state of open-hackathon server

    Attributes:
        OK: open-hackathon server API is running
        WARNING: open-hackathon server is running but something might be wrong, some feature may not work
        ERROR: open-hackathon server is unavailable
    """
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


class HEALTH:
    """Constants for health check"""
    STATUS = "status"
    DESCRIPTION = "description"
    VERSION = "version"


class HACKATHON_STAT:
    """Statistics types of a hackathon

    Attributes:
        LIKE: number of user that likes a hackathon
        REGISTER: number of registered users
    """
    LIKE = "like"
    REGISTER = "register"


class HACKATHON_BASIC_INFO:
    """Basic settings of hackathon that saved into column 'basic_info' of table 'hackathon'

    Attributes:
        LOCATION: str|unicode, the location where the hackathon is held
        MAX_ENROLLMENT: int, maximum users allowed to register
        AUTO_APPROVE: bool, whether manual approve is required, default false
        RECYCLE_ENABLED: bool, whether environment be recycled automatically. default false
        RECYCLE_MINUTES: int, the maximum time (unit:minute) of recycle for per experiment. default 0
        PRE_ALLOCATE_ENABLED: bool, whether to pre-start several environment. default false
        PRE_ALLOCATE_NUMBER: int, the maximum count of pre-start environment per hackathon and per template. default 1
        PRE_ALLOCATE_INTERVAL_SECONDS: int, interval seconds for pre-allocate job
        ALAUDA_ENABLED: bool,default false, whether to use alauda service, no azure resource needed if true
        FREEDOM_TEAM: bool,default true,Whether to allow freedom of the team
    """
    LOCATION = "location"
    MAX_ENROLLMENT = "max_enrollment"
    AUTO_APPROVE = "auto_approve"
    RECYCLE_ENABLED = "recycle_enabled"
    RECYCLE_MINUTES = "recycle_minutes"
    PRE_ALLOCATE_ENABLED = "pre_allocate_enabled"
    PRE_ALLOCATE_NUMBER = "pre_allocate_number"
    PRE_ALLOCATE_INTERVAL_SECONDS = "pre_allocate_interval_second"
    ALAUDA_ENABLED = "alauda_enabled"
    FREEDOM_TEAM = "freedom_team"


class CLOUD_ECLIPSE:
    """CloudEclipse Constans"""
    CLOUD_ECLIPSE = "cloud_eclipse"


class TEMPLATE_STATUS:
    """Status for db model Template

    Attributes:
        UNCHECKED: status of an new template that has not been tested
        CHECK_PASS: status indicates an validated template
        CHECK_FAILED: status
    """
    # todo template test not ready
    UNCHECKED = 0
    CHECK_PASS = 1
    CHECK_FAILED = 2


class VE_PROVIDER:
    """VirtualEnvironment provider in db model VirtualEnvironment and Template

    Attributes:
        DOCKER: VirtualEnvironment is based on docker. Docker host can be any cloud such as azure, aws or others
        CHECK_PASS: VirtualEnvironment is based on azure vm usually a windows VE
        CHECK_FAILED: VirtualEnvironment is based on Alauda web service
    """
    DOCKER = 0
    AZURE = 1
    ALAUDA = 2


class AZURE_RESOURCE_TYPE:
    """Resource type used by ALOperation(Azure log operation)"""
    STORAGE_ACCOUNT = 'storage account'
    CLOUD_SERVICE = 'cloud service'
    DEPLOYMENT = 'deployment'
    VIRTUAL_MACHINE = 'virtual machine'


class EStatus:
    """Status for db model Experiment"""
    INIT = 0
    STARTING = 1
    RUNNING = 2
    STOPPED = 3
    DELETED = 4
    FAILED = 5
    ROLL_BACKING = 6
    ROLL_BACKED = 7
    UNEXPECTED_ERROR = 8


class VEStatus:
    """Status for VirtualEnvironment"""
    INIT = 0
    RUNNING = 1
    FAILED = 2
    STOPPED = 3
    DELETED = 4
    UNEXPECTED_ERROR = 5


class PortBindingType:
    """Type of port binding

    Attributes:
        CloudService: type indicates public endpoint on cloudService
        DOCKER: type indicates exposed port on docker host machine
    """
    CLOUD_SERVICE = 1
    DOCKER = 2


class VERemoteProvider:
    """Remote provider type in db model VirtualEnvironment that indicates how to connect to a remote VE"""
    Guacamole = 0


class EmailStatus:
    """Status of email

    primary means the most used or important email of user. For example, you can add several email to your github account,
    but only one of them is primary, and it's the only one that github notifications are sent to.

    Attributes:
        NonPrimary: it's user's non-primary email
        Primary: it's user's primary email
    """
    NonPrimary = 0
    Primary = 1


class ReservedUser:
    """Special user of open-hackathon system.

    Attributes:
        DefaultUserID: a virtual user_id that when user_id cannot be empty but no actual user is related. For example,
    The pre-allocated experiments belong to DefaultUserID
        DefaultSuperAdmin: the default super admin that is initialized during the first DB setup which has the superior
    admin privilege.
    """
    DefaultUserID = -1
    DefaultSuperAdmin = 1


class ALOperation:
    """
    For operation in db model AzureLog
    """
    CREATE = 'create'
    CREATE_STORAGE_ACCOUNT = CREATE + ' ' + AZURE_RESOURCE_TYPE.STORAGE_ACCOUNT
    CREATE_CLOUD_SERVICE = CREATE + ' ' + AZURE_RESOURCE_TYPE.CLOUD_SERVICE
    CREATE_DEPLOYMENT = CREATE + ' ' + AZURE_RESOURCE_TYPE.DEPLOYMENT
    CREATE_VIRTUAL_MACHINE = CREATE + ' ' + AZURE_RESOURCE_TYPE.VIRTUAL_MACHINE
    STOP = 'stop'
    STOP_VIRTUAL_MACHINE = STOP + ' ' + AZURE_RESOURCE_TYPE.VIRTUAL_MACHINE
    START = 'start'
    START_VIRTUAL_MACHINE = START + AZURE_RESOURCE_TYPE.VIRTUAL_MACHINE


class ALStatus:
    """
    For status in db model AzureLog
    """
    START = 'start'
    FAIL = 'fail'
    END = 'end'


class ASAStatus:
    """
    For status in db model AzureStorageAccount
    """
    ONLINE = 'Online'


class ACSStatus:
    """
    For status in db model AzureCloudService
    """
    CREATED = 'Created'


class ADStatus:
    """
    For status in db model AzureDeployment
    """
    RUNNING = 'Running'


class AVMStatus:
    """
    For status in db model AzureVirtualMachine
    """
    READY_ROLE = 'ReadyRole'
    STOPPED_VM = 'StoppedVM'
    STOPPED = 'Stopped'  # STOPPED is only used for 'type' input parameter of stop_virtual_machine in VirtualMachine
    STOPPED_DEALLOCATED = 'StoppedDeallocated'


class RGStatus:
    """
    For status in DB model Register for registration audit status
    """
    UNAUDIT = 0
    AUDIT_PASSED = 1
    AUDIT_REFUSE = 2
    AUTO_PASSED = 3


class ADMIN_ROLE_TYPE:
    """
    admin role types
    """
    ADMIN = 1
    JUDGE = 2


class ORGANIZATION_TYPE:
    """
    Organization role type
    """
    ORGANIZER = 1
    PARTNER = 2


class HACK_STATUS:
    INIT = 0
    ONLINE = 1
    OFFLINE = 2


class HACK_TYPE:
    """
    For type in db model Hackathon
    """
    HACKATHON = 1
    CONTEST = 2


class FILE_TYPE:
    """Type of file to be saved into storage

    File of different types may saved in different position
    """
    TEMPLATE = "template"
    HACK_IMAGE = "hack_image"
    AZURE_CERT = "azure_cert"


class TeamMemberStatus:
    """Status of member of team

    Attributes:
        Init: A newly team member that wants to join the team
        Approved: member approved by team leader or system administrator
        Denied: member denied by team leader or system administrator. Member of this status won't be saved in DB
    """
    Init = 0
    Approved = 1
    Denied = 2


class DockerHostServerStatus:
    """
    Status of docker host server VM

    Attributes:
        STARTING: VM is in the process of starting
        DOCKER_INIT: VM starts successfully according to the feedback of Azure and docker application is in the process
                     of initialization
        DOCKER_READY: VM docker api port is OK
        UNAVAILABLE: VM is unavailable
    """
    STARTING = 0
    DOCKER_INIT = 1
    DOCKER_READY = 2
    UNAVAILABLE = 3


class DockerHostServerDisable:
    """
    whether the docker host server VM is disabled by manager or not

    Attributes:
        ABLE: VM is not disabled by manager
        DISABLE: VM is disabled by manager
    """
    ABLE = 0
    DISABLE = 1


class AzureVMStartMethod:
    """
    the way how Azure VM is started

    Attributes:
        AUTO: VM is started by OHP server
        MANUAL: VM is started manually
    """
    AUTO = 1
    MANUAL = 2


class AzureApiExceptionMessage:
    """
    The message returned by azure api when exception occurs

    Attributes:
        SERVICE_NOT_FOUND: the service is not found
        DEPLOYMENT_NOT_FOUND: the service deployment is not found
        CONTAINER_NOT_FOUND: the container is not found
    """
    SERVICE_NOT_FOUND = 'Not found (Not Found)'
    DEPLOYMENT_NOT_FOUND = 'Not found (Not Found)'
    CONTAINER_NOT_FOUND = 'Not found (The specified container does not exist.)'


class AzureOperationStatus:
    """
    The status of Azure operation

    Attributes:
        IN_PROGRESS: the operation is in process
        SUCCESS: the operation is successful
    """
    IN_PROGRESS = 'InProgress'
    SUCCESS = 'Succeeded'


class ServiceDeploymentSlot:
    """
    the slot of service deployment

    Attributes:
        PRODUCTION: production slot
        STAGING: staging slot
    """
    PRODUCTION = 'production'
    STAGING = 'staging'


class AzureVMSize:
    """
    the size of Azure VM

    Attributes:
        MEDIUM_SIZE: medium size
        SMALL_SIZE: small size
    """
    MEDIUM_SIZE = 'Medium'
    SMALL_SIZE = 'Small'


class AzureVMEndpointName:
    """
    the name of Azure VM endpoint

    Attributes:
        DOCKER: docker
        SSH: ssh
        HTTP: http
    """
    DOCKER = 'docker'
    SSH = 'SSH'
    HTTP = 'http'


class AzureVMEndpointDefaultPort:
    """
    default local port (private port) of applications in Azure VM

    Attributes:
        DOCKER: the default local port of docker
        SSH: the default local port of SSH
    """
    DOCKER = 4243
    SSH = 22


class TCPProtocol:
    """
    the protocol of TCP layer

    Attributes:
        TCP: tcp protocol
        UDP: udp protocol
    """
    TCP = 'tcp'
    UDP = 'udp'


class DockerPingResult:
    """
    the response of ping docker public port

    Attributes:
        OK: the response content is 'OK'
    """
    OK = 'OK'


class AzureVMPowerState:
    """
    the state of Azure VM power

    Attributes:
        VM_STARTED: the VM is started
    """
    VM_STARTED = 'started'


class AzureVMEnpointConfigType:
    """
    the type of Azure VM endpoint configuration

    Attributes:
        NETWORK: type is 'NetworkConfiguration'
    """
    NETWORK = 'NetworkConfiguration'


class Team_Show_Type:
    """Type of resource to be shown. """
    Image = 0  # image
    Video = 1  # e.g. Youku link
    SourceCode = 2  # e.g. github
    PowerPoint = 3  # ppt
    Excel = 4  # excel
    Word = 5  # word
    Pdf = 6  # pdf
    Other = 99  # other


class LOGIN_PROVIDER:
    LIVE = 1
    GITHUB = 2
    QQ = 4
    WEIBO = 8
    GITCAFE = 16
    ALAUDA = 32


class HACK_NOTICE_CATEGORY:
    HACKATHON = 0  # hackathon related notice
    USER = 1   # user related notice
    EXPERIMENT = 2   # experiment related notice
    AWARD = 3 # award related notice
    TEMPLATE = 4  # template related notice


class HACK_NOTICE_EVENT:
    MANUAL = 0  # manually created hackatohon notice
    HACK_CREATE = 1
    HACK_EDIT = 2
    HACK_ONLINE = 3
    HACK_OFFLINE = 4 # hackathon create/edit/online/offline
    EXPR_JOIN = 5 # user start to program
