# -*- coding: utf-8 -*-
"""
Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
 
The MIT License (MIT)
 
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.util import undefined
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import os
from pytz import utc
from log import log
from hackathon_factory import RequiredFeature
from hackathon.util import safe_get_config, get_config, get_now
from datetime import timedelta
import inspect


def scheduler_listener(event):
    if event.code == EVENT_JOB_ERROR:
        print('The job crashed :(')
        log.warn("The schedule job crashed because of %s" % repr(event.exception))
    else:
        print('The job executed :)')
        log.debug("The schedule job %s executed and return value is '%s'" % (event.job_id, event.retval))


def scheduler_executor(feature, method, context):
    log.debug("prepare to execute '%s.%s' with context: %s" % (feature, method, context))

    inst = RequiredFeature(feature)
    mtd = getattr(inst, method)
    args_len = len(inspect.getargspec(mtd).args)

    if args_len < 2:
        mtd()
    else:
        mtd(context)


class HackathonScheduler():
    jobstore = None

    def __init__(self, app):
        self.app = app
        self.__apscheduler = None

        if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            self.__apscheduler = BackgroundScheduler(timezone=utc)

            # job store
            if safe_get_config("scheduler.job_store", "memory") == "mysql":
                self.jobstore = 'sqlalchemy'
                self.__apscheduler.add_jobstore(self.jobstore, url=get_config("scheduler.job_store_url"))

            # listener
            # do we need listen EVENT_JOB_MISSED?
            self.__apscheduler.add_listener(scheduler_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
            log.info("APScheduler loaded")
            self.__apscheduler.start()

    def get_scheduler(self):
        return self.__apscheduler

    def add_once(self, feature, method, context=None, id=None, replace_existing=True, run_date=None, **delta):
        if not run_date:
            run_date = get_now() + timedelta(**delta)

        if self.__apscheduler:
            self.__apscheduler.add_job(scheduler_executor,
                                       trigger='date',
                                       run_date=run_date,
                                       id=id,
                                       max_instances=1,
                                       replace_existing=replace_existing,
                                       args=[feature, method, context])

    def add_interval(self, feature, method, id=None, context=None, replace_existing=True, next_run_time=undefined,
                     **interval):
        if self.__apscheduler:
            self.__apscheduler.add_job(scheduler_executor,
                                       trigger='interval',
                                       id=id,
                                       max_instances=1,
                                       replace_existing=replace_existing,
                                       next_run_time=next_run_time,
                                       args=[feature, method, context],
                                       **interval)

    def remove_job(self, job_id):
        if self.__apscheduler:
            try:
                self.__apscheduler.remove_job(job_id, self.jobstore)
            except JobLookupError:
                log.debug("remove job failed because job %s not found" % job_id)
            except Exception as e:
                log.error(e)
