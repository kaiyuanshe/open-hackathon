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

from hackathon_factory import RequiredFeature
from datetime import timedelta
from hackathon.scheduler import scheduler
from hackathon.database.models import Template, Experiment
from hackathon.enum import EStatus, VEProvider, ReservedUser


log = RequiredFeature("log")
util = RequiredFeature("util")
hackathon_manager = RequiredFeature("hackathon_manager")
expr_manager = RequiredFeature("expr_manager")
db = RequiredFeature("db")
template_manager = RequiredFeature("template_manager")
docker = RequiredFeature("docker")

# --------------------------------------------- job function definition ---------------------------------------------#

def check_default_expr():
    # only deal with online hackathons
    hackathon_id_list = hackathon_manager.get_pre_allocate_enabled_hackathon_list()
    templates = db.find_all_objects_order(Template, Template.hackathon_id.in_(hackathon_id_list))
    for template in templates:
        try:
            pre_num = hackathon_manager.get_pre_allocate_number(template.hackathon)
            curr_num = db.count(Experiment,
                                Experiment.user_id == ReservedUser.DefaultUserID,
                                Experiment.template_id == template.id,
                                (Experiment.status == EStatus.Starting) | (
                                    Experiment.status == EStatus.Running))
            # todo test azure, config num
            if template.provider == VEProvider.AzureVM:
                if curr_num < pre_num:
                    remain_num = pre_num - curr_num
                    start_num = db.count_by(Experiment,
                                            user_id=ReservedUser.DefaultUserID,
                                            template=template,
                                            status=EStatus.Starting)
                    if start_num > 0:
                        log.debug("there is an azure env starting, will check later ... ")
                        return
                    else:
                        log.debug("no starting template: %s , remain num is %d ... " % (template.name, remain_num))
                        expr_manager.start_expr(template.hackathon.name, template.name, ReservedUser.DefaultUserID)
                        break
                        # curr_num += 1
                        # self.log.debug("all template %s start complete" % template.name)
            elif template.provider == VEProvider.Docker:
                log.debug("template name is %s, hackathon name is %s" % (template.name, template.hackathon.name))
                if curr_num < pre_num:
                    remain_num = pre_num - curr_num
                    log.debug("no idle template: %s, remain num is %d ... " % (template.name, remain_num))
                    expr_manager.start_expr(template.hackathon.name, template.name, ReservedUser.DefaultUserID)
                    # curr_num += 1
                    break
                    # self.log.debug("all template %s start complete" % template.name)
        except Exception as e:
            log.error(e)
            log.error("check default experiment failed")


def recycle_expr():
    """
    recycle experiment when idle more than 24 hours
    :return:
    """
    log.debug("start checking experiment ... ")
    recycle_hours = util.safe_get_config('recycle.idle_hours', 24)

    expr_time_cond = Experiment.last_heart_beat_time + timedelta(hours=recycle_hours) > util.get_now()
    recycle_cond = Experiment.hackathon_id.in_(hackathon_manager.get_recyclable_hackathon_list())
    r = db.find_first_object(Experiment, hackathon_manager, expr_time_cond, recycle_cond)

    if r is not None:
        expr_manager.stop_expr(r.id)
        log.debug("it's stopping " + str(r.id) + " inactive experiment now")
    else:
        log.debug("There is now inactive experiment now")
        return


def auto_pull_images_for_hackathon(hackathon):
    return template_manager.pull_images_for_hackathon(hackathon)


def docker_pull_image(docker_host, image, tag):
    return docker.pull_image(docker_host, image, tag)


# --------------------------------------------- job callable functions ---------------------------------------------#

def open_check_expr():
    """
    start a scheduled job to examine default experiment
    :return:
    """
    alarm_time = util.get_now() + timedelta(seconds=1)
    scheduler.add_job(check_default_expr, 'interval', id='pre', replace_existing=True, next_run_time=alarm_time,
                      minutes=util.safe_get_config("pre_allocate.check_interval_minutes", 5))


def recycle_expr_scheduler():
    """
    start a scheduled job to recycle inactive experiment
    :return:
    """
    excute_time = util.get_now() + timedelta(minutes=10)
    scheduler.add_job(recycle_expr, 'interval', id='recycle', replace_existing=True, next_run_time=excute_time,
                      minutes=util.safe_get_config("recycle.check_idle_interval_minutes", 5))


def ensure_images():
    hackathons = hackathon_manager.get_online_hackthons()
    # TODO check hackathon VirtualEvironment provider is docker
    for hackathon in hackathons:
        log.debug("Start recycling inactive ensure images for hackathons")
        excute_time = util.get_now() + timedelta(seconds=3)
        scheduler.add_job(auto_pull_images_for_hackathon,
                          'interval',
                          id='%s pull images' % hackathon.id,
                          replace_existing=True,
                          next_run_time=excute_time,
                          minutes=60,
                          args=[hackathon])
    log.debug("starting to release ports ... ")


# ------------------------------- Run jobs withn API service starting ---------------------------------------------#

def start_init_job():
    open_check_expr()
    recycle_expr_scheduler()
    ensure_images()