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

import sys

sys.path.append("..")
from health_check import *
from datetime import datetime

app_start_time = datetime.utcnow();

all_health_items = {
    "mysql": MySQLHealthCheck(),
    "docker": DockerHealthCheck(),
    "guacamole": GuacamoleHealthCheck(),
    "azure": AzureHealthCheck()
}

basic_health_items = {
    "mysql": MySQLHealthCheck(),
    "guacamole": GuacamoleHealthCheck()
}


def __report_detail(health, items):
    for key, value in items.iteritems():
        sub_report = value.reportHealth()
        health[key] = sub_report
        if sub_report[STATUS] != HEALTH_STATE.OK and health[STATUS] != HEALTH_STATE.ERROR:
            health[STATUS] = sub_report[STATUS]
    return health


def report_health(q):
    items = basic_health_items
    if q == "all":
        items = all_health_items
    elif q in all_health_items.keys():
        items = {
            q: all_health_items[q]
        }

    up = datetime.utcnow() - app_start_time
    days, hours, minutes = up.days, up.seconds / 3600, up.seconds % 3600 / 60.0
    health = {
        STATUS: HEALTH_STATE.OK,
        "start_time": str(app_start_time),
        "report_time": str(datetime.utcnow()),
        "up": "%d days %d hours %d miutes" % (days, hours, minutes)
    }

    __report_detail(health, items)

    return health
