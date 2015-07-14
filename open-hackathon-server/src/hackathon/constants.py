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


class HEALTH_STATE:
    """The running state of open-hackathon server

    Attributes:
        OK: open-hackathon server API is running
        WARNING: open-hackathon server is running but something might be wrong, some feature may not work
        ERROR: open-hackathon server is unavailable
    """
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


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
    PRE_ALLOCATE_ENABLED = "pre_allocate_enabled"
    PRE_ALLOCATE_NUMBER = "pre_allocate_number"
    ALAUDA_ENABLED = "alauda_enabled"


class CLOUD_ECLIPSE:
    """CloudEclipse Constans"""
    CLOUD_ECLIPSE = "cloud_eclipse"
