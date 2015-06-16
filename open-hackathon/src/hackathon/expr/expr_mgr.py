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

from hackathon import (
    Component,
    RequiredFeature,
)

from hackathon.enum import (
    EStatus,
    VERemoteProvider,
    VEProvider,
    PortBindingType,
    VEStatus,
    ReservedUser,
    AVMStatus,
)
from hackathon.database.models import (
    VirtualEnvironment,
    DockerHostServer,
    Experiment,
    Hackathon,
    Template,
)

from hackathon.azureformation.azureFormation import (
    AzureFormation,
)

from hackathon.hackathon_response import (
    internal_server_error,
    precondition_failed,
    not_found,
    access_denied,
    ok,
)

from hackathon.template.docker_template_unit import (
    DockerTemplateUnit,
)
from hackathon.template.base_template import (
    BaseTemplate,
)
import json
import random
import string
from sqlalchemy import (
    and_,
)
from hackathon.initialise_jobs import (
    open_check_expr
)


class ExprManager(Component):
    register_manager = RequiredFeature("register_manager")
    hackathon_manager = RequiredFeature("hackathon_manager")
    template_manager = RequiredFeature("template_manager")
    docker = RequiredFeature("docker")

    def start_expr(self, hackathon_name, template_name, user_id):
        """
        A user uses a template to start a experiment under a hackathon
        :param hackathon_name:
        :param template_name:
        :param user_id:
        :return:
        """
        hack_temp = self.__check_template_status(hackathon_name, template_name)
        if hack_temp is None:
            return not_found('hackathon or template is not existed')

        hackathon = hack_temp[0]
        if not self.register_manager.is_user_registered(user_id, hackathon):
            return access_denied("user not registered or not approved")

        if hackathon.event_end_time < self.util.get_now():
            self.log.warn("hackathon is ended. The expr starting process will be stopped")
            return precondition_failed('hackathen is ended')

        template = hack_temp[1]

        if user_id > 0:
            expr = self.__check_expr_status(user_id, hackathon, template)
            if expr is not None:
                return self.__report_expr_status(expr)

        # new expr
        return self.__start_new_expr(hackathon, template, user_id)

    def heart_beat(self, expr_id):
        expr = self.db.find_first_object_by(Experiment, id=expr_id, status=EStatus.Running)
        if expr is None:
            return not_found('Experiment does not running')

        expr.last_heart_beat_time = self.util.get_now()
        self.db.commit()
        return ok('OK')

    def stop_expr(self, expr_id, force=0):
        """
        :param expr_id: experiment id
        :param force: 0: only stop container and release ports, 1: force stop and delete container and release ports.
        :return:
        """
        self.log.debug("begin to stop %d" % expr_id)
        expr = self.db.find_first_object_by(Experiment, id=expr_id, status=EStatus.Running)
        if expr is not None:
            # Docker
            if expr.template.provider == VEProvider.Docker:
                # stop containers
                for c in expr.virtual_environments.all():
                    try:
                        self.log.debug("begin to stop %s" % c.name)
                        if force:
                            self.docker.delete(c.name, virtual_environment=c, container=c.container, expr_id=expr_id)
                            c.status = VEStatus.Deleted
                        else:
                            self.docker.stop(c.name, virtual_environment=c, container=c.container, expr_id=expr_id)
                            c.status = VEStatus.Stopped
                    except Exception as e:
                        self.log.error(e)
                        self.__roll_back(expr_id)
                        return internal_server_error('Failed stop/delete container')
                if force:
                    expr.status = EStatus.Deleted
                else:
                    expr.status = EStatus.Stopped
                self.db.commit()
            else:
                try:
                    # todo support delete azure vm
                    af = AzureFormation(self.docker.__load_azure_key_id(expr_id))
                    af.stop(expr_id, AVMStatus.STOPPED_DEALLOCATED)
                except Exception as e:
                    self.log.error(e)
                    return internal_server_error('Failed stopping azure')

            self.log.debug("experiment %d ended success" % expr_id)
            return ok('OK')
        else:
            return ok('expr not exist')

    def get_expr_status(self, expr_id):
        expr = self.db.find_first_object_by(Experiment, id=expr_id)
        if expr is not None:
            return self.__report_expr_status(expr)
        else:
            return not_found('Experiment Not found')

    def get_expr_list_by_user_id(self, user_id):
        return map(lambda u: u.dic(),
                   self.db.find_all_objects(Experiment, and_(Experiment.user_id == user_id, Experiment.status < 5)))

    # --------------------------------------------- helper function ---------------------------------------------#

    def __start_new_expr(self, hackathon, template, user_id):
        # new expr
        expr = self.db.add_object_kwargs(Experiment,
                                         user_id=user_id,
                                         hackathon_id=hackathon.id,
                                         status=EStatus.Init,
                                         template_id=template.id)
        self.db.commit()

        curr_num = self.db.count(Experiment,
                                 Experiment.user_id == ReservedUser.DefaultUserID,
                                 Experiment.template == template,
                                 (Experiment.status == EStatus.Starting) |
                                 (Experiment.status == EStatus.Running))
        if template.provider == VEProvider.Docker:
            try:
                template_dic = json.load(file(template.url))
                virtual_environments_list = template_dic[BaseTemplate.VIRTUAL_ENVIRONMENTS]
                if curr_num != 0 and curr_num >= self.util.get_config("pre_allocate.docker"):
                    return
                expr.status = EStatus.Starting
                self.db.commit()
                map(lambda virtual_environment_dic:
                    self.__remote_start_container(hackathon, expr, virtual_environment_dic),
                    virtual_environments_list)
                expr.status = EStatus.Running
                self.db.commit()
            except Exception as e:
                self.log.error(e)
                self.log.error("Failed starting containers")
                self.__roll_back(expr.id)
                return internal_server_error('Failed starting containers')
        else:
            if curr_num != 0 and curr_num >= self.util.get_config("pre_allocate.azure"):
                return
            expr.status = EStatus.Starting
            self.db.commit()
            try:
                af = AzureFormation(self.docker.__load_azure_key_id(expr.id))
                af.create(expr.id)
            except Exception as e:
                self.log.error(e)
                return internal_server_error('Failed starting azure vm')
        # after everything is ready, set the expr state to running
        # response to caller
        return self.__report_expr_status(expr)

    def __report_expr_status(self, expr):
        ret = {
            "expr_id": expr.id,
            "status": expr.status,
            "hackathon": expr.hackathon.name,
            "create_time": str(expr.create_time),
            "last_heart_beat_time": str(expr.last_heart_beat_time),
        }
        if expr.status != EStatus.Running:
            return ret
        # return guacamole link to frontend
        guacamole_servers = []
        for ve in expr.virtual_environments.all():
            if ve.remote_provider == VERemoteProvider.Guacamole:
                guacamole_config = json.loads(ve.remote_paras)
                guacamole_host = self.util.safe_get_config("guacamole.host", "localhost:8080")
                # target url format:
                # http://localhost:8080/guacamole/#/client/c/{name}?name={name}&oh={token}
                name = guacamole_config["name"]
                url = guacamole_host + '/guacamole/#/client/c/%s?name=%s' % (name, name)
                guacamole_servers.append({
                    "name": guacamole_config["displayname"],
                    "url": url
                })
        if expr.status == EStatus.Running:
            ret["remote_servers"] = guacamole_servers
        # return public accessible web url
        public_urls = []
        if expr.template.provider == VEProvider.Docker:
            for ve in expr.virtual_environments.all():
                for p in ve.port_bindings.all():
                    if p.binding_type == PortBindingType.CloudService and p.url is not None:
                        hs = self.db.find_first_object_by(DockerHostServer, id=p.binding_resource_id)
                        url = p.url.format(hs.public_dns, p.port_from)
                        public_urls.append({
                            "name": p.name,
                            "url": url
                        })
        else:
            for ve in expr.virtual_environments.all():
                for vm in ve.azure_virtual_machines_v.all():
                    ep = vm.azure_endpoints.filter_by(private_port=80).first()
                    url = 'http://%s:%s' % (vm.public_ip, ep.public_port)
                    public_urls.append({
                        "name": ep.name,
                        "url": url
                    })
        ret["public_urls"] = public_urls
        return ret

    def __check_template_status(self, hackathon_name, template_name):
        hackathon = self.db.find_first_object_by(Hackathon, name=hackathon_name)
        if hackathon is None:
            return None
        template = self.db.find_first_object_by(Template, hackathon=hackathon, name=template_name)
        if template is None or self.template_manager.load_template(template) is None:
            return None
        return [hackathon, template]

    def __remote_start_container(self, hackathon, expr, virtual_environment_dic):
        docker_template_unit = DockerTemplateUnit(virtual_environment_dic)
        old_name = docker_template_unit.get_name()
        suffix = "".join(random.sample(string.ascii_letters + string.digits, 8))
        new_name = '%d-%s-%s' % (expr.id, old_name, suffix)
        docker_template_unit.set_name(new_name)
        self.log.debug("starting to start container: %s" % new_name)
        # db entity
        ve = VirtualEnvironment(provider=VEProvider.Docker,
                                name=new_name,
                                image=docker_template_unit.get_image_with_tag(),
                                status=VEStatus.Init,
                                remote_provider=VERemoteProvider.Guacamole,
                                experiment=expr)
        self.db.add_object(ve)

        # start container remotely
        container_ret = self.docker.start(docker_template_unit,
                                          hackathon=hackathon,
                                          virtual_environment=ve,
                                          experiment=expr)
        if container_ret is None:
            self.log.error("container %s fail to run" % new_name)
            raise Exception("container_ret is none")
        ve.status = VEStatus.Running
        self.db.commit()
        self.log.debug("starting container %s is ended ... " % new_name)
        return ve

    def __check_expr_status(self, user_id, hackathon, template):
        """
        check experiment status, if there are pre-allocate experiments, the experiment will be assigned directly
        :param user_id:
        :param hackathon:
        :param template:
        :return:
        """
        exp_status = [EStatus.Running, EStatus.Starting]
        check_temp = Experiment.template_id == template.id if self.hackathon_manager.validate_admin_privilege(user_id,hackathon.id) else Experiment.id > -1
        expr = self.db.find_first_object(Experiment,
                                         Experiment.status.in_(exp_status),
                                         Experiment.user_id == user_id,
                                         Experiment.hackathon_id == hackathon.id,
                                         check_temp)
        if expr is not None:
            return expr

        expr = self.db.find_first_object_by(Experiment,
                                            status=EStatus.Running,
                                            hackathon_id=hackathon.id,
                                            user_id=ReservedUser.DefaultUserID,
                                            template=template)
        if expr is not None:
            self.db.update_object(expr, user_id=user_id)
            self.db.commit()
            self.log.debug("experiment had been assigned, check experiment and start new job ... ")

            # add a job to start new pre-allocate experiment
            open_check_expr()
            return expr

    def __roll_back(self, expr_id):
        """
        roll back when exception occurred
        :param expr_id: experiment id
        """
        self.log.debug("Starting rollback ...")
        expr = self.db.find_first_object_by(Experiment, id=expr_id)
        try:
            expr.status = EStatus.Rollbacking
            self.db.commit()
            if expr is not None:
                # delete containers and change expr status
                for c in expr.virtual_environments:
                    if c.provider == VEProvider.Docker:
                        self.docker.delete(c.name, container=c.container, expr_id=expr_id)
                        c.status = VEStatus.Deleted
                        self.db.commit()
            # delete ports
            expr.status = EStatus.Rollbacked

            self.db.commit()
            self.log.info("Rollback succeeded")
        except Exception as e:
            expr.status = EStatus.Failed
            self.db.commit()
            self.log.info("Rollback failed")
            self.log.error(e)

            # --------------------------------------------- helper function ---------------------------------------------#

