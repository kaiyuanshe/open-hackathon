# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import os
from pytz import utc
from datetime import timedelta
import inspect

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.util import undefined
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_ADDED

from hackathon.hackathon_factory import RequiredFeature
from hackathon.util import safe_get_config, get_config, get_now
from hackathon.log import log
from hackathon.config import Config

__all__ = ["HackathonScheduler"]


def scheduler_listener(event):
    """Custom listener for apscheduler

    Will write the details to log file in case apscheduler job succeeds or error occurs

    :param event: the event executed and related to the apscheduler job
    """
    if event.code == EVENT_JOB_ERROR:
        log.debug('The job crashed :(')
        log.warn("The schedule job crashed because of %s" % repr(event.exception))
    elif event.code == EVENT_JOB_ADDED:
        log.debug("job added %s" % event.job_id)
    else:
        log.debug('The job executed :)')
        log.debug("The schedule job %s executed and return value is '%s'" % (event.job_id, event.retval))


def scheduler_executor(feature, method, context):
    """task for all apscheduler jobs

    While the context of apscheduler job will be serialized and saved into MySQL, it's hard that add an instance method
    as an apscheduler job because the context is usually very complicate and not easy to be serialized. For example, see
    we want to add an new job to execute 'user_mgr.get_user_info' in 5 minutes, then the whole 'user_mgr' which involves
    many other classes will be serialized and saved which probably fail for many of them including 'user_mgr' itself are
    not serializable.

    However functions are much easier, that's why we define function 'scheduler_executor' out of any class. It acts as a
    redirect engine. We find the method that the job really want to execute and then call it.

    :type feature: str|unicode
    :param feature: the instance key for hackathon_factory.

    :type method: str|unicode
    :param method: the name of method related to instance

    :type context: Context, see definition in hackathon/__init__.py
    :param context: the expected execution context of target method
    """
    log.debug("prepare to execute '%s.%s' with context: %s" % (feature, method, context))
    inst = RequiredFeature(feature)
    mtd = getattr(inst, method)
    args_len = len(inspect.getargspec(mtd).args)

    if args_len < 2:
        # if target method doesn't expect any parameter except 'self', the args_len is 1
        mtd()
    else:
        # call with execution context
        mtd(context)


class HackathonScheduler(object):
    """An helper class for apscheduler"""
    jobstore = "ohp"

    def get_scheduler(self):
        """Return the apscheduler instance in case you have to call it directly

        :return the instance of APScheduler

        .. notes:: the return value might be None in flask debug mode
        """
        return self.__apscheduler

    def add_once(self, feature, method, context=None, id=None, replace_existing=True, run_date=None, **delta):
        """Add a job to APScheduler and executed only once

        Job will be executed at 'run_date' or after certain timedelta.

        :Example:
            scheduler = RequiredFeature("scheduler")

            # execute task once in 5 minutes:
            context = Context(user_id=1)
            scheduler.add_once("user_manager","get_user_by_id",context=context, minutes=5)
            # 5 minutes later, user_manager.get_user_by_id(context) will be executed

        :type feature: str|unicode
        :param: the feature that are used to look for instance through hackathon_factory. All features are defined in __init__.py

        :type method: str|unicode
        :param method: the method name defined in the instance

        :type context: Context, see hackathon/__init__.py
        :param context: the execution context. Actually the parameters of 'method'

        :type id: str
        :param id: id for APScheduler job. Random id will be generated if not specified by caller

        :type replace_existing: bool
        :param replace_existing: if true, existing job with the same id will be replaced. If false, exception will be raised

        :type run_date: datetime | None
        :param run_date: job run date. If None, job run date will be datetime.now()+timedelta(delta)

        :type delta: kwargs for timedelta
        :param delta: kwargs for timedelta. For example: minutes=5. Will be ignored if run_date is not None
        """
        if not run_date:
            run_date = get_now() + timedelta(**delta)

        if self.__apscheduler:
            self.__apscheduler.add_job(scheduler_executor,
                                       trigger='date',
                                       run_date=run_date,
                                       id=id,
                                       max_instances=1,
                                       replace_existing=replace_existing,
                                       jobstore=self.jobstore,
                                       args=[feature, method, context])

    def add_interval(self, feature, method, context=None, id=None, replace_existing=True, next_run_time=undefined,
                     **interval):
        """Add an interval job to APScheduler and executed.

        Job will be executed firstly at 'next_run_time'. And then executed in interval.

        :Example:
            scheduler = RequiredFeature("scheduler")

            context = Context(user_id=1)
            scheduler.add_interval("user_manager","get_user_by_id", context=context, minutes=10)
            # user_manager.get_user_by_id(context) will be called every 10 minutes

        :type feature: str|unicode
        :param: the feature that are used to look for instance through hackathon_factory. All features are defined in __init__.py

        :type method: str|unicode
        :param method: the method name defined in the instance

        :type context: Context, see hackathon/__init__.py
        :param context: the execution context. Actually the parameters of 'method'

        :type id: str
        :param id: id for APScheduler job. Random id will be generated if not specified by caller

        :type replace_existing: bool
        :param replace_existing: if true, existing job with the same id will be replaced. If false, exception will be raised

        :type next_run_time: datetime | undefined
        :param next_run_time: the first time the job will be executed. leave undefined to don't execute until interval time reached

        :type interval: kwargs for "interval" trigger
        :param interval: kwargs for "interval" trigger. For example: minutes=5.
        """
        if self.__apscheduler:
            self.__apscheduler.add_job(scheduler_executor,
                                       trigger='interval',
                                       id=id,
                                       max_instances=1,
                                       replace_existing=replace_existing,
                                       next_run_time=next_run_time,
                                       jobstore=self.jobstore,
                                       args=[feature, method, context],
                                       **interval)

    def remove_job(self, job_id):
        """Remove job from APScheduler job store

        :type job_id: str | unicode
        :param job_id: the id of job
        """
        if self.__apscheduler:
            try:
                self.__apscheduler.remove_job(job_id, self.jobstore)
            except JobLookupError:
                log.debug("remove job failed because job %s not found" % job_id)
            except Exception as e:
                log.error(e)

    def has_job(self, job_id):
        """Check the existence of specific job """
        if self.__apscheduler:
            job = self.__apscheduler.get_job(job_id, jobstore=self.jobstore)
            return job is not None
        return False

    def __init__(self, app):
        """Initialize APScheduler

        :type app: Flask
        :param app: the Flask app
        """
        self.app = app
        self.__apscheduler = None

        # NOT instantiate while in flask DEBUG mode or in the main thread
        # It's to avoid APScheduler being instantiated twice
        if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            self.__apscheduler = BackgroundScheduler(timezone=utc)

            # add MySQL job store
            job_store_type = safe_get_config("scheduler.job_store", "memory")
            if job_store_type == "mysql":
                log.debug("add aps_cheduler job store based on mysql")
                self.__apscheduler.add_jobstore('sqlalchemy',
                                                alias=self.jobstore,
                                                url=get_config("scheduler.job_store_url"))
            elif job_store_type == "mongodb":
                # safe_get_config
                log.debug("add aps_cheduler job store based on mongodb")
                self.__apscheduler.add_jobstore('mongodb',
                                                alias=self.jobstore,
                                                database=Config.get("scheduler").get("database"),
                                                collection=Config.get('scheduler').get('collection'),
                                                host=Config.get("scheduler").get("host"),
                                                port=Config.get("scheduler").get("port"))
            # add event listener
            self.__apscheduler.add_listener(scheduler_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_ADDED)
            log.info("APScheduler loaded")
            self.__apscheduler.start()
