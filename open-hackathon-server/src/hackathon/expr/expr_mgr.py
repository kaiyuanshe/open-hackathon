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
from datetime import timedelta

from werkzeug.exceptions import PreconditionFailed, NotFound
from mongoengine import Q

from hackathon import Component, RequiredFeature, Context
from hackathon.constants import EStatus, VERemoteProvider, VE_PROVIDER, VEStatus, ReservedUser, \
    HACK_NOTICE_EVENT, HACK_NOTICE_CATEGORY, CLOUD_PROVIDER, HACKATHON_CONFIG
from hackathon.hmongo.models import Experiment, User, Hackathon, UserHackathon
from hackathon.hackathon_response import not_found, ok

__all__ = ["ExprManager"]


class ExprManager(Component):
    user_manager = RequiredFeature("user_manager")
    hackathon_manager = RequiredFeature("hackathon_manager")
    admin_manager = RequiredFeature("admin_manager")
    template_library = RequiredFeature("template_library")

    def start_expr(self, user, template_name, hackathon_name=None):
        """
        A user uses a template to start a experiment under a hackathon
        :param hackathon_name:
        :param template_name:
        :param user_id:
        :return:
        """

        self.log.debug("try to start experiment for hackathon %s using template %s" % (hackathon_name, template_name))
        hackathon = self.__verify_hackathon(hackathon_name)
        template = self.__verify_template(hackathon, template_name)

        if user:
            expr = self.__check_expr_status(user, hackathon, template)
            if expr:
                return self.__report_expr_status(expr)

        # new expr
        return self.__start_new_expr(hackathon, template, user)

    def heart_beat(self, expr_id):
        expr = Experiment.objects(id=expr_id, status=EStatus.RUNNING).first()
        if expr is None:
            return not_found('Experiment is not running')

        expr.last_heart_beat_time = self.util.get_now()
        expr.save()
        return ok()

    def stop_expr(self, expr_id):
        """
        :param expr_id: experiment id
        :return:
        """
        self.log.debug("begin to stop %s" % str(expr_id))
        expr = Experiment.objects(id=expr_id, status=EStatus.RUNNING).first()
        if expr is not None:
            starter = self.get_starter(expr.hackathon, expr.template)
            if starter:
                starter.stop_expr(Context(experiment_id=expr.id, experiment=expr))
            self.log.debug("experiment %s ended success" % expr_id)
            return ok('OK')
        else:
            return ok()

    def get_expr_status(self, expr_id):
        expr = Experiment.objects(id=expr_id).first()
        if expr:
            return self.__report_expr_status(expr)
        else:
            return not_found('Experiment Not found')

    def check_expr_status(self, experiment):
        # update experiment status
        virtual_environment_list = experiment.virtual_environments
        if all(x.status == VEStatus.RUNNING for x in virtual_environment_list) \
                and len(virtual_environment_list) == experiment.template.virtual_environment_count:
            experiment.status = EStatus.RUNNING
            experiment.save()
            try:
                self.template_library.template_verified(experiment.template.id)
            except:
                pass

    def get_expr_list_by_hackathon_id(self, hackathon, context):
        # get a list of all experiments' detail
        user_name = context.user_name if "user_name" in context else None
        status = context.status if "status" in context else None
        page = int(context.page) if "page" in context else 1
        per_page = int(context.per_page) if "per_page" in context else 10
        users = User.objects(name=user_name).all() if user_name else []

        if user_name and status:
            experiments_pagi = Experiment.objects(hackathon=hackathon, status=status, user__in=users).paginate(page, per_page)
        elif user_name and not status:
            experiments_pagi = Experiment.objects(hackathon=hackathon, user__in=users).paginate(page, per_page)
        elif not user_name and status:
            experiments_pagi = Experiment.objects(hackathon=hackathon, status=status).paginate(page, per_page)
        else:
            experiments_pagi = Experiment.objects(hackathon=hackathon).paginate(page, per_page)

        return self.util.paginate(experiments_pagi, self.__get_expr_with_detail)

    def scheduler_recycle_expr(self):
        """recycle experiment according to hackathon basic info on recycle configuration

        According to the hackathon's basic info on 'recycle_enabled', find out time out experiments
        Then call function to recycle them

        :return:
        """
        self.log.debug("start checking recyclable experiment ... ")
        for hackathon in self.hackathon_manager.get_recyclable_hackathon_list():
            try:
                # check recycle enabled
                mins = self.hackathon_manager.get_recycle_minutes(hackathon)
                # filter out the experiments that need to be recycled
                exprs = Experiment.objects(create_time__lt=self.util.get_now() - timedelta(minutes=mins),
                                           status=EStatus.RUNNING,
                                           hackathon=hackathon)
                for expr in exprs:
                    self.__recycle_expr(expr)
            except Exception as e:
                self.log.error(e)

    def pre_allocate_expr(self, context):
        # TODO: too complex, not check
        hackathon_id = context.hackathon_id
        self.log.debug("executing pre_allocate_expr for hackathon %s " % hackathon_id)
        hackathon = Hackathon.objects(id=hackathon_id).first()
        hackathon_templates = hackathon.templates
        for template in hackathon_templates:
            try:
                template = template
                pre_num = int(hackathon.config.get("pre_allocate_number", 1))
                query = Q(status=EStatus.STARTING) | Q(status=EStatus.RUNNING)
                curr_num = Experiment.objects(user=None, hackathon=hackathon, template=template).filter(query).count()
                if template.provider == VE_PROVIDER.AZURE:
                    if curr_num < pre_num:
                        remain_num = pre_num - curr_num
                        start_num = Experiment.objects(user=None, template=template, status=EStatus.STARTING).count()
                        if start_num > 0:
                            self.log.debug("there is an azure env starting, will check later ... ")
                            return
                        else:
                            self.log.debug(
                                "no starting template: %s , remain num is %d ... " % (template.name, remain_num))
                            self.start_expr(None, template.name, hackathon.name)
                            break
                elif template.provider == VE_PROVIDER.DOCKER:
                    if hackathon.config.get('cloud_provider') == CLOUD_PROVIDER.ALAUDA:
                        # don't create pre-env if alauda used
                        continue

                    self.log.debug(
                        "template name is %s, hackathon name is %s" % (template.name, hackathon.name))
                    if curr_num < pre_num:
                        remain_num = pre_num - curr_num
                        start_num = Experiment.objects(user=None, template=template, status=EStatus.STARTING).count()
                        if start_num > 0:
                            self.log.debug("there is an docker container starting, will check later ... ")
                            return
                        self.log.debug("no idle template: %s, remain num is %d ... " % (template.name, remain_num))
                        self.start_expr(None, template.name, hackathon.name)
                        break
            except Exception as e:
                self.log.error(e)
                self.log.error("check default experiment failed")

    def assign_expr_to_admin(self, expr):
        """assign expr to admin to trun expr into pre_allocate_expr

        :type expr: Experiment
        :param expr: which expr you want to assign

        :return:
        """
        expr.user = None
        expr.save()

    # --------------------------------------------- helper function ---------------------------------------------#

    def __verify_hackathon(self, hackathon_name):
        """validate the event_start_time and event_end_time of a hackathon

        Will return None if hackathon not found or current time is not between its start time and end time
        """
        hackathon = self.hackathon_manager.get_hackathon_by_name(hackathon_name)
        if hackathon:
            if HACKATHON_CONFIG.CLOUD_PROVIDER not in hackathon.config:
                raise PreconditionFailed("No cloud resource is configured for this hackathon.")
            if self.util.get_now() < hackathon.event_end_time:
                return hackathon
            else:
                raise PreconditionFailed("Hackathon was already ended")
        else:
            raise NotFound("Hackathon with name %s not found" % hackathon_name)

    def get_starter(self, hackathon, template):
        # load expr starter
        starter = None
        if not hackathon or not template:
            return starter

        if template.provider == VE_PROVIDER.DOCKER:
            if HACKATHON_CONFIG.CLOUD_PROVIDER in hackathon.config:
                if hackathon.config[HACKATHON_CONFIG.CLOUD_PROVIDER] == CLOUD_PROVIDER.AZURE:
                    starter = RequiredFeature("azure_docker")
                elif hackathon.config[HACKATHON_CONFIG.CLOUD_PROVIDER] == CLOUD_PROVIDER.ALAUDA:
                    starter = RequiredFeature("alauda_docker")
        elif template.provider == VE_PROVIDER.AZURE:
            starter = RequiredFeature("azure_vm")

        return starter

    def __start_new_expr(self, hackathon, template, user):
        starter = self.get_starter(hackathon, template)

        if not starter:
            raise PreconditionFailed("either template not supported or hackathon resource not configured")

        context = starter.start_expr(Context(
            template=template,
            user=user,
            hackathon=hackathon))

        return self.__report_expr_status(context.experiment)

    def on_expr_started(self, experiment):
        hackathon = experiment.hackathon
        user = experiment.user

    def __report_expr_status(self, expr):
        ret = {
            "expr_id": str(expr.id),
            "status": expr.status,
            "hackathon_name": expr.hackathon.name if expr.hackathon else "",
            "hackathon": str(expr.hackathon.id) if expr.hackathon else "",
            "create_time": str(expr.create_time),
            "last_heart_beat_time": str(expr.last_heart_beat_time)}

        if expr.status != EStatus.RUNNING:
            return ret

        # return remote clients include guacamole
        remote_servers = []
        for ve in expr.virtual_environments:
            if ve.remote_provider == VERemoteProvider.Guacamole:
                try:
                    guacamole_config = ve.remote_paras
                    guacamole_host = self.util.safe_get_config("guacamole.host", "localhost:8080")
                    # target url format:
                    # http://localhost:8080/guacamole/#/client/c/{name}?name={name}&oh={token}
                    name = guacamole_config["name"]
                    url = guacamole_host + '/guacamole/#/client/c/%s?name=%s' % (name, name)
                    remote_servers.append({
                        "name": guacamole_config["name"],
                        "guacamole_host": guacamole_host,
                        "url": url})

                except Exception as e:
                    self.log.error(e)
                    # so that the frontend can query again?
                    ret["status"] = EStatus.STARTING
                    return ret

        ret["remote_servers"] = remote_servers

        # return public accessible web url
        public_urls = []
        if expr.template.provider == VE_PROVIDER.DOCKER:
            for ve in expr.virtual_environments:
                container = ve.docker_container
                for p in container.port_bindings.filter(is_public=True):
                    if p.url:
                        public_urls.append({
                            "name": p.name,
                            "url": p.url.format(container.host_server.public_dns, p.public_port)})
        else:
            for ve in expr.virtual_environments:
                vm = ve.azure_resource
                if not vm or not vm.end_points:
                    continue

                for endpoint in vm.end_points:
                    if endpoint.url:
                        public_urls.append({
                            "name": endpoint.name,
                            "url": endpoint.url.format(vm.dns, endpoint.public_port)
                        })

        ret["public_urls"] = public_urls
        return ret

    def __verify_template(self, hackathon, template_name):
        template = self.template_library.get_template_info_by_name(template_name)
        if not template:
            raise NotFound("template cannot be found by name '%s'" % template_name)

        if not hackathon:
            # hackathon is None means it's starting expr for template testing
            return template

        hackathon_templates = hackathon.templates
        template_ids = [t.id for t in hackathon_templates]
        if template.id not in template_ids:
            raise PreconditionFailed("template '%s' not allowed for hackathon '%s'" % (template_name, hackathon.name))

        return template

    def __check_expr_status(self, user, hackathon, template):
        """
        check experiment status, if there are pre-allocate experiments, the experiment will be assigned directly
        :param user:
        :param hackathon:
        :param template:
        :return:
        """
        criterion = Q(status__in=[EStatus.RUNNING, EStatus.STARTING], hackathon=hackathon, user=user)
        is_admin = self.admin_manager.is_hackathon_admin(hackathon.id, user.id)
        if is_admin:
            criterion &= Q(template=template)

        expr = Experiment.objects(criterion).first()
        if expr:
            # user has a running/starting experiment
            return expr

        # try to assign pre-configured expr to user
        expr = Experiment.objects(status=EStatus.RUNNING, hackathon=hackathon, template=template, user=None).first()
        if expr:
            expr.user = user
            expr.save()
            return expr

    def roll_back(self, expr_id):
        """
        roll back when exception occurred
        :param expr_id: experiment id
        """
        self.log.debug("Starting rollback experiment %s..." % expr_id)
        expr = Experiment.objects(id=expr_id)
        if not expr:
            self.log.warn("rollback failed due to experiment not found")
            return

        starter = self.get_starter(expr.hackathon, expr.template)
        if not starter:
            self.log.warn("rollback failed due to no starter found")
            return

        return starter.rollback(Context(experiment=expr))

    def __get_expr_with_detail(self, experiment):
        info = experiment.dic()
        # replace OjbectId with user info
        info['user'] = self.user_manager.user_display_info(experiment.user)
        return info

    def __recycle_expr(self, expr):
        """recycle expr

        If it is a docker experiment , stop it ; else assign it to default user

        :type expr: Experiment
        :param expr: the exper which you want to recycle

        :return:
        """
        providers = map(lambda x: x.provider, expr.virtual_environments)
        if VE_PROVIDER.DOCKER in providers:
            self.stop_expr(expr.id)
            self.log.debug("it's stopping " + str(expr.id) + " inactive experiment now")
        else:
            self.assign_expr_to_admin(expr)
            self.log.debug("assign " + str(expr.id) + " to default admin")
