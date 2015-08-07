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


class HACKATHON_BASIC_INFO:
    """Basic settings of hackathon that saved into column 'basic_info' of table 'hackathon'

    Attributes:
        ORGANIZERS: array [{ organizer_name:'' , organizer_url:'',  organizer_image:'',organizer_description:''},...]
        ORGANIZER_NAME: str|unicode, name of organizer
        ORGANIZER_URL: str|unicode, url link to the organizer. For example its homepage
        ORGANIZER_IMAGE: str|unicode, logo of the organizer. We don't store the image itself, just a link to target
        ORGANIZER_DESCRIPTION: str|unicode, description of the organizer.
        BANNERS: array ['banner_image_url',...], array of images as banners for the hackathon
        LOCATION: str|unicode, the location where the hackathon is held
        MAX_ENROLLMENT: int, maximum users allowed to register
        WALL_TIME: long, environment will be auto recycled, in seconds
        AUTO_APPROVE: bool, whether manual approve is required, default false
        RECYCLE_ENABLED: bool, whether environment be recycled automatically. default false
        RECYCLE_MINUTES: int, the maximum time (unit:minute) of recycle for per experiment. default 0
        PRE_ALLOCATE_ENABLED: bool, whether to pre-start several environment. default false
        PRE_ALLOCATE_NUMBER: int, the maximum count of pre-start environment per hackathon and per template. default 1
        ALAUDA_ENABLED: bool,default false, whether to use alauda service, no azure resource needed if true
    """
    ORGANIZERS = "organizers"
    ORGANIZER_NAME = "organizer_name"
    ORGANIZER_URL = "organizer_url"
    ORGANIZER_IMAGE = "organizer_image"
    ORGANIZER_DESCRIPTION = "organizer_description"
    BANNERS = "banners"
    LOCATION = "location"
    MAX_ENROLLMENT = "max_enrollment"
    WALL_TIME = "wall_time"
    AUTO_APPROVE = "auto_approve"
    RECYCLE_ENABLED = "recycle_enabled"
    RECYCLE_MINUTES = "recycle_minutes"
    PRE_ALLOCATE_ENABLED = "pre_allocate_enabled"
    PRE_ALLOCATE_NUMBER = "pre_allocate_number"
    ALAUDA_ENABLED = "alauda_enabled"


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
