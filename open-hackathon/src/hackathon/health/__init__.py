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
        if sub_report[STATUS] != HEALTH_STATE.OK:
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
    days, hours, minutes = up.days, up.seconds // 3600, up.seconds % 3600 / 60.0
    health = {
        STATUS: HEALTH_STATE.OK,
        "start_time": str(app_start_time),
        "report_time": str(datetime.utcnow()),
        "up": "%d days %d hours %d miutes" % (days, hours, minutes)
    }

    __report_detail(health, items)

    return health
