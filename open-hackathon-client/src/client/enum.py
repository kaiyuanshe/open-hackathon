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

class ExprStatus:
    Init = 0
    Starting = 1
    Running = 2
    Stopped = 3
    Deleted = 4
    Failed = 5
    Rollbacking = 6
    Rollbacked = 7


class VirtualEnvStatus:
    Init = 0
    Running = 1
    Stopped = 2
    Deleted = 3


class PortBindingType:
    CloudService = 1
    Docker = 2


class VirtualEnvironmentProvider:
    AzureVM = "azure-vm"
    Docker = "docker"


class RemoteProvider:
    Guacamole = "guacamole"


class EmailStatus:
    Primary = 1
    NonPrimary = 0


class LoginProvider:
    live = 1
    github = 2
    qq = 4
    weibo = 8
    # gitcafe = 16 no longer support
    alauda = 32
    wechat = 64
