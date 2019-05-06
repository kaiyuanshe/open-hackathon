# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import sys

sys.path.append("..")
from datetime import timedelta

from werkzeug.exceptions import PreconditionFailed, NotFound
from mongoengine import Q

from hackathon import Component, RequiredFeature, Context
from hackathon.constants import EStatus, VERemoteProvider, VE_PROVIDER, VEStatus, ReservedUser, \
    HACK_NOTICE_EVENT, HACK_NOTICE_CATEGORY, CLOUD_PROVIDER, HACKATHON_CONFIG
from hackathon.hmongo.models import Experiment, User, Hackathon, UserHackathon, Template
from hackathon.hackathon_response import not_found, ok

__all__ = ["ExprManager"]


class ExprManager(Component):
    user_manager = RequiredFeature("user_manager")
    hackathon_manager = RequiredFeature("hackathon_manager")
    admin_manager = RequiredFeature("admin_manager")
    template_library = RequiredFeature("template_library")
    hosted_docker_proxy = RequiredFeature("hosted_docker_proxy")

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


    def restart_stopped_expr(self, experiment_id):
        # todo: now just support hosted_docker, not support for alauda and windows
        experiment = Experiment.objects(id=experiment_id).first()
        for ve in experiment.virtual_environments:
            if ve.provider == VE_PROVIDER.DOCKER:
                if not self.hosted_docker_proxy.is_container_running(ve.docker_container):
                    self.hosted_docker_proxy.start_container(ve.docker_container.host_server,
                                                             ve.docker_container.container_id)
            elif ve.provider == VE_PROVIDER.ALAUDA:
                pass
            elif ve.provider == VE_PROVIDER.AZURE:
                pass
        self.__check_expr_real_status(experiment)
        return experiment.dic()

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
        expr = Experiment.objects(id=expr_id).first()
        if expr is not None:
            starter = self.get_starter(expr.hackathon, expr.template)
            if starter:
                starter.stop_expr(Context(experiment_id=expr.id, experiment=expr))
            self.log.debug("experiment %s ended success" % expr_id)
            return ok('OK')
        else:
            return ok()

    def get_expr_status_and_confirm_starting(self, expr_id):
        expr = Experiment.objects(id=expr_id).first()
        if expr:
            return self.__report_expr_status(expr, isToConfirmExprStarting=True)
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
            experiments_pagi = Experiment.objects(hackathon=hackathon, status=status, user__in=users).paginate(page,
                                                                                                               per_page)
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
        template = hackathon_templates[0]
        query = Q(status=EStatus.STARTING) | Q(status=EStatus.RUNNING)

        pre_num = int(hackathon.config.get("pre_allocate_number", 1))
        curr_num = Experiment.objects(user=None, hackathon=hackathon, template=template).filter(query).count()
        self.log.debug("pre_alloc_exprs: pre_num is %d, curr_num is %d, remain_num is %d " % (pre_num, curr_num, pre_num - curr_num))

        if curr_num < pre_num:
            self.start_pre_alloc_exprs(None, template.name, hackathon.name, pre_num - curr_num)

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

        # TODO Interim workaround for kubernetes, need real implementation
        if hackathon.config.get('cloud_provider') == CLOUD_PROVIDER.KUBERNETES:
            return RequiredFeature("k8s_service")

        if template.provider == VE_PROVIDER.DOCKER:
            if HACKATHON_CONFIG.CLOUD_PROVIDER in hackathon.config:
                if hackathon.config[HACKATHON_CONFIG.CLOUD_PROVIDER] == CLOUD_PROVIDER.AZURE:
                    starter = RequiredFeature("azure_docker")
                elif hackathon.config[HACKATHON_CONFIG.CLOUD_PROVIDER] == CLOUD_PROVIDER.ALAUDA:
                    starter = RequiredFeature("alauda_docker")
        elif template.provider == VE_PROVIDER.AZURE:
            starter = RequiredFeature("azure_vm")
        elif template.provider == VE_PROVIDER.K8S:
            starter = RequiredFeature("k8s_service")

        return starter

    def __start_new_expr(self, hackathon, template, user):
        starter = self.get_starter(hackathon, template)

        if not starter:
            raise PreconditionFailed("either template not supported or hackathon resource not configured")

        context = starter.start_expr(Context(
            template=template,
            user=user,
            hackathon=hackathon,
            pre_alloc_enabled = False))

        return self.__report_expr_status(context.experiment)

    def start_pre_alloc_exprs(self, user, template_name, hackathon_name=None, pre_alloc_num = 0):
        self.log.debug("start_pre_alloc_exprs: %d " % pre_alloc_num)
        if pre_alloc_num == 0: return

        hackathon = self.__verify_hackathon(hackathon_name)
        template = self.__verify_template(hackathon, template_name)


        starter = self.get_starter(hackathon, template)
        if not starter:
            raise PreconditionFailed("either template not supported or hackathon resource not configured")

        while pre_alloc_num > 0:
            context = starter.start_expr(Context(
                template=template,
                user=user,
                hackathon=hackathon,
                pre_alloc_enabled = True))

            if context == None:
                self.log.debug("pre_alloc_num left: %d " % pre_alloc_num)
                break
            else:
                self.__report_expr_status(context.experiment)
                pre_alloc_num -= 1

    def on_expr_started(self, experiment):
        hackathon = experiment.hackathon
        user = experiment.user

    def __report_expr_status(self, expr, isToConfirmExprStarting=False):
        # todo check whether need to restart Window-expr and Alauda-expr if it shutdown
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
                        "display_name": guacamole_config["displayname"],
                        "guacamole_host": guacamole_host,
                        "url": url})

                except Exception as e:
                    self.log.error(e)
                    # so that the frontend can query again?
                    ret["status"] = EStatus.STARTING
                    return ret

        ret["remote_servers"] = remote_servers

        # return public accessible web url
        ve_provider = expr.virtual_environments[0].provider
        public_urls = []
        if ve_provider == VE_PROVIDER.DOCKER:
            for ve in expr.virtual_environments:
                container = ve.docker_container
                # to restart hosted_docker expr if it stopped.
                if isToConfirmExprStarting:
                    if not self.hosted_docker_proxy.is_container_running(container):
                        self.hosted_docker_proxy.start_container(container.host_server, container.container_id)

                for p in container.port_bindings.filter(is_public=True):
                    if p.url:
                        public_urls.append({
                            "name": p.name,
                            "url": p.url.format(container.host_server.public_dns, p.public_port)})
        elif ve_provider == VE_PROVIDER.AZURE:
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
        elif ve_provider == VE_PROVIDER.K8S:
            # TODO public accessible http url
            public_urls.append({
                "name": "码云操作说明",
                "url": "http://www.ubuntukylin.com/public/pdf/gitee.pdf"
            })
            public_urls.append({
                "name": "Github操作说明",
                "url": "http://www.ubuntukylin.com/public/pdf/github.pdf"
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
        self.__check_expr_real_status(experiment)
        info = experiment.dic()
        # replace OjbectId with user info
        info['user'] = self.user_manager.user_display_info(experiment.user)
        return info

    def __check_expr_real_status(self, experiment):
        # todo: it is only support for hosted_docker right now. Please support Window-expr and Alauda-expr in future
        for ve in experiment.virtual_environments:
            if ve.provider == VE_PROVIDER.DOCKER:
                if not self.hosted_docker_proxy.is_container_running(ve.docker_container):
                    if ve.status == VEStatus.RUNNING:
                        ve.status = VEStatus.STOPPED
                else:
                    if ve.status == VEStatus.STOPPED:
                        ve.status = VEStatus.RUNNING
            elif ve.provider == VE_PROVIDER.ALAUDA:
                pass
            elif ve.provider == VE_PROVIDER.AZURE:
                pass
        if all(ve.status == VEStatus.STOPPED for ve in experiment.virtual_environments):
            experiment.status = EStatus.STOPPED
        if all(ve.status == VEStatus.RUNNING for ve in experiment.virtual_environments):
            experiment.status = EStatus.RUNNING
        experiment.update_time = self.util.get_now()
        experiment.save()

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
