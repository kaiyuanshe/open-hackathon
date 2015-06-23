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
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.util import undefined
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import os
from pytz import utc
from hackathon_factory import RequiredFeature
from datetime import timedelta


def scheduler_listener(event):
    log = RequiredFeature("log")

    if event.code == EVENT_JOB_ERROR:
        print('The job crashed :(')
        log.warn("The schedule job crashed because of %s" % repr(event.exception))
    else:
        print('The job executed :)')
        log.debug("The schedule job %s executed and return value is '%s'" % (event.job_id, event.retval))


def scheduler_executor(feature, method, context):
    inst = RequiredFeature(feature)
    mtd = getattr(inst, method)
    mtd(context)


class HackathonScheduler():
    log = RequiredFeature("log")
    util = RequiredFeature("util")

    def __init__(self, app):
        self.app = app

        if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            self.scheduler = BackgroundScheduler(timezone=utc)

            # job store
            if self.util.safe_get_config("scheduler.job_store", "memory") == "mysql":
                self.scheduler.add_jobstore('sqlalchemy', url=self.util.get_config("scheduler.job_store_url"))

            # listener
            # do we need listen EVENT_JOB_MISSED?
            self.scheduler.add_listener(scheduler_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
            self.scheduler.start()

    def get_scheduler(self):
        return self.scheduler

    def set_time(self, feature, method, context=None, id=None, replace_existing=True, run_date=None, **delta):
        if not run_date:
            run_date = self.util.get_now() + timedelta(**delta)

        self.scheduler.add_job(scheduler_executor,
                               trigger='date',
                               run_date=run_date,
                               id=id,
                               replace_existing=replace_existing,
                               args=[feature, method, context])

    def set_interval(self, feature, method, id=None, context=None, replace_existing=True, next_run_time=undefined,
                     **interval):
        self.scheduler.add_job(scheduler_executor,
                               trigger='interval',
                               id=id,
                               replace_existing=replace_existing,
                               next_run_time=next_run_time,
                               args=[feature, method, context],
                               **interval)
