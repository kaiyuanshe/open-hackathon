from functions import safe_get_config, get_config
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from . import app
import os
from log import log


def scheduler_listener(event):
    if event.code == EVENT_JOB_ERROR:
        print('The job crashed :(')
        log.warn("The schedule job crashed because of %s" % repr(event.exception))
    else:
        print('The job executed :)')
        log.debug("The schedule job %s executed and return value is '%s'" % (event.job_id, event.retval))


if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    scheduler = BackgroundScheduler()

    # job store
    if safe_get_config("scheduler.job_store", "memory") == "mysql":
        scheduler.add_jobstore('sqlalchemy', url=get_config("scheduler.job_store_url"))

    # listener
    # do we need listen EVENT_JOB_MISSED?
    scheduler.add_listener(scheduler_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    scheduler.start()

