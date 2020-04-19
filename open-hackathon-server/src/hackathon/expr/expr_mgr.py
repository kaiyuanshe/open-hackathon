# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""
from datetime import timedelta

from werkzeug.exceptions import PreconditionFailed, NotFound
from mongoengine import Q

from hackathon import Component, RequiredFeature
from hackathon.constants import EStatus, VERemoteProvider, VE_PROVIDER, VEStatus, HACKATHON_CONFIG
from hackathon.hmongo.models import Experiment, User
from hackathon.hackathon_response import not_found, ok
from hackathon.worker.expr_tasks import start_new_expr, stop_expr

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
        experiment = Experiment.objects(id=experiment_id).first()
        for ve in experiment.virtual_environments:
            if ve.provider == VE_PROVIDER.DOCKER:
                if not self.hosted_docker_proxy.is_container_running(ve.docker_container):
                    self.hosted_docker_proxy.start_container(ve.docker_container.host_server,
                                                             ve.docker_container.container_id)
            elif ve.provider == VE_PROVIDER.AZURE:
                raise NotImplementedError()

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
            hackathon = expr.hackathon
            stop_expr.delay(str(hackathon.id), str(expr.id))
            self.log.debug("experiment %s ended success" % expr_id)
            return ok('OK')
        else:
            return ok()

    def get_expr_status_and_confirm_starting(self, expr_id):
        expr = Experiment.objects(id=expr_id).first()
        if not expr:
            return not_found('Experiment Not found')
        return self.__report_expr_status(expr, isToConfirmExprStarting=True)

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

    def __start_new_expr(self, hackathon, template, user):
        expr = Experiment(
            status=EStatus.INIT,
            template=template,
            user=user,
            virtual_environments=[],
            hackathon=hackathon)
        expr.save()

        template_content = self.template_library.load_template(template)
        start_new_expr.delay(str(hackathon.id), str(expr.id), template_content)

        return self.__report_expr_status(expr)

    def start_pre_alloc_exprs(self, template_name, hackathon_name=None, pre_alloc_num=0):
        self.log.debug("start_pre_alloc_exprs: %d " % pre_alloc_num)
        try_create = 0
        if pre_alloc_num == 0:
            return try_create

        hackathon = self.__verify_hackathon(hackathon_name)
        template = self.__verify_template(hackathon, template_name)
        template_content = self.template_library.load_template(template)

        while pre_alloc_num > try_create:
            expr = Experiment(status=EStatus.INIT,
                              template=template,
                              virtual_environments=[],
                              hackathon=hackathon)
            expr.save()
            start_new_expr.delay(str(hackathon.id), str(expr.id), template_content)
            try_create += 1
        self.log.debug("start_pre_alloc_exprs: finish")
        return try_create

    def __report_expr_status(self, expr, isToConfirmExprStarting=False):
        # todo check whether need to restart Window-expr if it shutdown
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
        elif ve.provider == VE_PROVIDER.AZURE:
            raise NotImplementedError()
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
            public_urls.append({
                "name": "黑客松活动问卷",
                "url": "https://www.wjx.cn/m/39517441.aspx"
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

        hackathon = expr.hackathon
        stop_expr.delay(str(hackathon.id), str(expr.id))

    def __get_expr_with_detail(self, experiment):
        self.__check_expr_real_status(experiment)
        info = experiment.dic()
        # replace OjbectId with user info
        info['user'] = self.user_manager.user_display_info(experiment.user)
        return info

    def __check_expr_real_status(self, experiment):
        # todo: it is only support for hosted_docker right now. Please support Window-expr in future
        for ve in experiment.virtual_environments:
            if ve.provider == VE_PROVIDER.DOCKER:
                if not self.hosted_docker_proxy.is_container_running(ve.docker_container):
                    if ve.status == VEStatus.RUNNING:
                        ve.status = VEStatus.STOPPED
                else:
                    if ve.status == VEStatus.STOPPED:
                        ve.status = VEStatus.RUNNING
            elif ve.provider == VE_PROVIDER.AZURE:
                raise NotImplementedError()
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
        providers = [x.provider for x in expr.virtual_environments]
        if VE_PROVIDER.DOCKER in providers:
            self.stop_expr(expr.id)
            self.log.debug("it's stopping " + str(expr.id) + " inactive experiment now")
        else:
            self.assign_expr_to_admin(expr)
            self.log.debug("assign " + str(expr.id) + " to default admin")
