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

from hackathon.util import get_now
from hackathon import RequiredFeature
from hackathon.constants import HEALTH_STATUS

__all__ = ["report_health"]


# the time when application starts
app_start_time = get_now()

STATUS = "status"

# all available health check items
all_health_items = {
    "docker": RequiredFeature("health_check_hosted_docker"),
    "alauda": RequiredFeature("health_check_alauda_docker"),
    "guacamole": RequiredFeature("health_check_guacamole"),
    "azure": RequiredFeature("health_check_azure"),
    "storage": RequiredFeature("storage"),
    "mongodb": RequiredFeature("health_check_mongodb")
}

# basic health check items which are fundamental for OHP
basic_health_items = {
    "mongodb": RequiredFeature("health_check_mongodb"),
    "guacamole": RequiredFeature("health_check_guacamole"),
    "storage": RequiredFeature("storage")
}


def __report_detail(health, items):
    """Report the details of health check item

    :type health: dict
    :param health: the overall health status

    :type items: dict
    :param items: a dict that contains all detail items to check

    :rtype dict
    :return health status including overall status and details of sub items
    """
    for key, value in items.iteritems():
        sub_report = value.report_health()
        health[key] = sub_report
        if sub_report[STATUS] != HEALTH_STATUS.OK and health[STATUS] != HEALTH_STATUS.ERROR:
            health[STATUS] = sub_report[STATUS]
    return health


def report_health(q):
    """Report health status of open hackathon server

    :type q: str|unicode
    :param q: the report type. Can be 'all' or None or a key of health item

    :rtype dict
    :return health status including overall status and details of sub items
    """
    items = basic_health_items
    if q == "all":
        items = all_health_items
    elif q in all_health_items.keys():
        items = {
            q: all_health_items[q]
        }

    up = get_now() - app_start_time
    days, hours, minutes = up.days, up.seconds / 3600, up.seconds % 3600 / 60.0
    health = {
        STATUS: HEALTH_STATUS.OK,
        "start_time": str(app_start_time),
        "report_time": str(get_now()),
        "up": "%d days %d hours %d minutes" % (days, hours, minutes)
    }

    return __report_detail(health, items)
