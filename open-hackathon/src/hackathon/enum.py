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

# resource type used by ALOperation
STORAGE_ACCOUNT = 'storage account'
CLOUD_SERVICE = 'cloud service'
DEPLOYMENT = 'deployment'
VIRTUAL_MACHINE = 'virtual machine'


class EStatus:
    """
    For status in db model Experiment
    """
    Init = 0
    Starting = 1
    Running = 2
    Stopped = 3
    Deleted = 4
    Failed = 5
    Rollbacking = 6
    Rollbacked = 7


class VEStatus:
    """
    For status in db model VirtualEnvironment
    """
    Init = 0
    Running = 1
    Stopped = 2
    Deleted = 3


class PortBindingType:
    CloudService = 1
    Docker = 2


class VEProvider:
    """
    For provider in db model VirtualEnvironment
    """
    AzureVM = 0
    Docker = 1


class VERemoteProvider:
    """
    For remote provider in db model VirtualEnvironment
    """
    Guacamole = 0


class EmailStatus:
    Primary = 1
    NonPrimary = 0


class ReservedUser:
    DefaultUserID = -1
    DockerVM = -2


class AdminUserHackathonRelStates:
    Actived = 1
    Disabled = 0

# ------------------------------ Enums are introduced by azure formation ------------------------------


class ALOperation:
    """
    For operation in db model AzureLog
    """
    CREATE = 'create'
    CREATE_STORAGE_ACCOUNT = CREATE + ' ' + STORAGE_ACCOUNT
    CREATE_CLOUD_SERVICE = CREATE + ' ' + CLOUD_SERVICE
    CREATE_DEPLOYMENT = CREATE + ' ' + DEPLOYMENT
    CREATE_VIRTUAL_MACHINE = CREATE + ' ' + VIRTUAL_MACHINE
    STOP = 'stop'
    STOP_VIRTUAL_MACHINE = STOP + ' ' + VIRTUAL_MACHINE
    START = 'start'
    START_VIRTUAL_MACHINE = START + VIRTUAL_MACHINE


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