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
    TOKEN = "token"
    HACKATHON_NAME = "hackathon_name"


class OAUTH_PROVIDER:
    GITHUB = "github"
    QQ = "qq"
    GITCAFE = "gitcafe"
    WEIBO = "weibo"


class HEALTH_STATE:
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


class ADMIN:
    SUPER_ADMIN_GROUP_ID = 1
    DEFAULT_SUPER_ADMIN_EMAIL = "2303202961@qq.com"


class HACKATHON_BASIC_INFO:
    ORGANIZERS = "organizers" #array  [{ organizer_name:'' , organizer_url:'',  organizer_image:'',organizer_description:''},...]
    ORGANIZER_NAME = "organizer_name" # string
    ORGANIZER_URL = "organizer_url" # string
    ORGANIZER_IMAGE = "organizer_image" # string
    ORGANIZER_DESCRIPTION = "organizer_description"  # string
    BANNERS = "banners"  # array ['banner_image_url',...]
    LOCATION = "location" # string location organizer 
    MAX_ENROLLMENT = "max_enrollment" # int
    WALL_TIME = "wall_time" # long 
    AUTO_APPROVE = "auto_approve"  # bool
    RECYCLE_ENABLED = "recycle_enabled"  #bool
