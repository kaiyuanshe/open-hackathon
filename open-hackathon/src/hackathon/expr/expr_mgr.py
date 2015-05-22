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
from hackathon.functions import get_now

sys.path.append("..")

from hackathon.docker.docker import (
    docker_formation,
)
from hackathon.functions import (
    safe_get_config,
    get_config,
)
from hackathon.scheduler import (
    scheduler,
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
    HackathonAzureKey,
    Experiment,
    PortBinding,
    DockerContainer,
    Hackathon,
    Template,
)
from hackathon.database import (
    db_adapter,
)
from hackathon.log import (
    log,
)
from hackathon.azureformation.service import (
    Service,
)
from hackathon.azureformation.endpoint import (
    Endpoint,
)
from hackathon.azureformation.azureFormation import (
    AzureFormation,
)
from datetime import (
    timedelta,
)
from hackathon.hackathon_response import (
    internal_server_error,
    precondition_failed,
    not_found,
    ok,
)
from hackathon.template.docker_template_unit import (
    DockerTemplateUnit,
)
from hackathon.template.base_template import (
    BaseTemplate,
)
from hackathon.hack import (
    hack_manager,
)
import json
import os
import random
import string


class ExprManager(object):

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
            return internal_server_error('hackathon or template is not existed')

        hackathon = hack_temp[0]
        if hackathon.event_end_time < datetime.utcnow():
            log.warn("hackathon is ended. The expr starting process will be stopped")
            return precondition_failed('hackathen is ended')

        template = hack_temp[1]
        if user_id > 0:
            expr = self.__check_expr_status(user_id, hackathon, template)
            if expr is not None:
                return self.__report_expr_status(expr)

        # new expr
        expr = db_adapter.add_object_kwargs(Experiment,
                                            user_id=user_id,
                                            hackathon_id=hackathon.id,
                                            status=EStatus.Init,
                                            template_id=template.id)
        db_adapter.commit()

        curr_num = db_adapter.count(Experiment,
                                    Experiment.user_id == ReservedUser.DefaultUserID,
                                    Experiment.template == template,
                                    (Experiment.status == EStatus.Starting) |
                                    (Experiment.status == EStatus.Running))
        if template.provider == VEProvider.Docker:
            try:
                template_dic = json.load(file(template.url))
                virtual_environments_list = template_dic[BaseTemplate.VIRTUAL_ENVIRONMENTS]
                host_server = self.__get_available_docker_host(len(virtual_environments_list), hackathon)
                if curr_num != 0 and curr_num >= get_config("pre_allocate.docker"):
                    return
                expr.status = EStatus.Starting
                db_adapter.commit()
                map(lambda virtual_environment_dic:
                    self.__remote_start_container(expr, host_server, virtual_environment_dic),
                    virtual_environments_list)
                expr.status = EStatus.Running
                db_adapter.commit()
            except Exception as e:
                log.error(e)
                log.error("Failed starting containers")
                self.__roll_back(expr.id)
                return internal_server_error('Failed starting containers')
        else:
            if curr_num != 0 and curr_num >= get_config("pre_allocate.azure"):
                return
            expr.status = EStatus.Starting
            db_adapter.commit()
            try:
                af = AzureFormation(self.__load_azure_key_id(expr.id))
                af.create(expr.id)
            except Exception as e:
                log.error(e)
                return internal_server_error('Failed starting azure vm')
        # after everything is ready, set the expr state to running
        # response to caller
        return self.__report_expr_status(expr)

    def heart_beat(self, expr_id):
        expr = db_adapter.find_first_object_by(Experiment, id=expr_id, status=EStatus.Running)
        if expr is None:
            return not_found('Experiment does not running')

        expr.last_heart_beat_time = get_now()
        db_adapter.commit()
        return ok('OK')

    def stop_expr(self, expr_id, force=0):
        """
        :param expr_id: experiment id
        :param force: 0: only stop container and release ports, 1: force stop and delete container and release ports.
        :return:
        """
        log.debug("begin to stop %d" % expr_id)
        expr = db_adapter.find_first_object_by(Experiment, id=expr_id, status=EStatus.Running)
        if expr is not None:
            # Docker
            if expr.template.provider == VEProvider.Docker:
                # stop containers
                for c in expr.virtual_environments:
                    try:
                        log.debug("begin to stop %s" % c.name)
                        if force:
                            docker_formation.delete(c.name, c.container.host_server)
                            c.status = VEStatus.Deleted
                        else:
                            docker_formation.stop(c.name, c.container.host_server)
                            c.status = VEStatus.Stopped
                        c.container.host_server.container_count -= 1
                        if c.container.host_server.container_count < 0:
                            c.container.host_server.container_count = 0
                        # self.__release_ports(expr_id, c.container.host_server)
                        self.__release_ports(expr_id, c.container.host_server)
                    except Exception as e:
                        log.error(e)
                        self.__roll_back(expr_id)
                        return internal_server_error('Failed stop/delete container')
                if force:
                    expr.status = EStatus.Deleted
                else:
                    expr.status = EStatus.Stopped
                db_adapter.commit()
            else:
                try:
                    # todo support delete azure vm
                    af = AzureFormation(self.__load_azure_key_id(expr_id))
                    af.stop(expr_id, AVMStatus.STOPPED_DEALLOCATED)
                except Exception as e:
                    log.error(e)
                    return internal_server_error('Failed stopping azure')

            log.debug("experiment %d ended success" % expr_id)
            return ok('OK')
        else:
            return ok('expr not exist')

    def get_expr_status(self, expr_id):
        expr = db_adapter.find_first_object_by(Experiment, id=expr_id)
        if expr is not None:
            return self.__report_expr_status(expr)
        else:
            return not_found('Experiment Not found')

    # --------------------------------------------- helper function ---------------------------------------------#

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
                guacamole_host = safe_get_config("guacamole.host", "localhost:8080")
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
                        hs = db_adapter.find_first_object_by(DockerHostServer, id=p.binding_resource_id)
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

    def __get_available_docker_host(self, req_count, hackathon):
        vm = db_adapter.find_first_object(DockerHostServer,
                                          DockerHostServer.container_count + req_count <=
                                          DockerHostServer.container_max_count,
                                          DockerHostServer.hackathon_id == hackathon.id)

        # todo connect to azure to launch new VM if no existed VM meet the requirement
        # since it takes some time to launch VM,
        # it's more reasonable to launch VM when the existed ones are almost used up.
        # The new-created VM must run 'cloudvm service by default(either cloud-init or python remote ssh)
        # todo the VM public/private IP will change after reboot, need sync the IP in db with azure in this case
        if vm is None:
            raise Exception("No available VM.")
        return vm

    def __load_azure_key_id(self, expr_id):
        expr = db_adapter.get_object(Experiment, expr_id)
        hak = db_adapter.find_first_object_by(HackathonAzureKey, hackathon_id=expr.hackathon_id)
        return hak.azure_key_id

    def __check_template_status(self, hackathon_name, template_name):
        hackathon = db_adapter.find_first_object_by(Hackathon, name=hackathon_name)
        if hackathon is None:
            return None
        template = db_adapter.find_first_object_by(Template, hackathon=hackathon, name=template_name)
        if template is None or not os.path.isfile(template.url):
            return None
        return [hackathon, template]

    def __get_available_public_ports(self, expr_id, host_server, host_ports):
        log.debug("starting to get azure ports")
        ep = Endpoint(Service(self.__load_azure_key_id(expr_id)))
        host_server_name = host_server.vm_name
        host_server_dns = host_server.public_dns.split('.')[0]
        public_endpoints = ep.assign_public_endpoints(host_server_dns, 'Production', host_server_name, host_ports)
        if not isinstance(public_endpoints, list):
            log.debug("failed to get public ports")
            return internal_server_error('cannot get public ports')
        log.debug("public ports : %s" % public_endpoints)
        return public_endpoints

    def __release_public_ports(self, expr_id, host_server, host_ports):
        ep = Endpoint(Service(self.__load_azure_key_id(expr_id)))
        host_server_name = host_server.vm_name
        host_server_dns = host_server.public_dns.split('.')[0]
        log.debug("starting to release ports ... ")
        ep.release_public_endpoints(host_server_dns, 'Production', host_server_name, host_ports)

    def __assign_ports(self, expr, host_server, ve, port_cfg):
        """
        assign ports from host server
        :param expr:
        :param host_server:
        :param ve:
        :param port_cfg:
        :return:
        """
        # get 'host_port'
        map(lambda p:
            p.update(
                {DockerTemplateUnit.PORTS_HOST_PORT: docker_formation.get_available_host_port(host_server, p[DockerTemplateUnit.PORTS_PORT])}
            ),
            port_cfg)

        # get 'public' cfg
        public_ports_cfg = filter(lambda p: DockerTemplateUnit.PORTS_PUBLIC in p, port_cfg)
        host_ports = [u[DockerTemplateUnit.PORTS_HOST_PORT] for u in public_ports_cfg]
        if safe_get_config("environment", "prod") == "local":
            map(lambda cfg: cfg.update({DockerTemplateUnit.PORTS_PUBLIC_PORT: cfg[DockerTemplateUnit.PORTS_HOST_PORT]}), public_ports_cfg)
        else:
            public_ports = self.__get_available_public_ports(expr.id, host_server, host_ports)
            for i in range(len(public_ports_cfg)):
                public_ports_cfg[i][DockerTemplateUnit.PORTS_PUBLIC_PORT] = public_ports[i]

        binding_dockers = []

        # update port binding
        for public_cfg in public_ports_cfg:
            binding_cloud_service = PortBinding(name=public_cfg[DockerTemplateUnit.PORTS_NAME],
                                                port_from=public_cfg[DockerTemplateUnit.PORTS_PUBLIC_PORT],
                                                port_to=public_cfg[DockerTemplateUnit.PORTS_HOST_PORT],
                                                binding_type=PortBindingType.CloudService,
                                                binding_resource_id=host_server.id,
                                                virtual_environment=ve,
                                                experiment=expr,
                                                url=public_cfg[DockerTemplateUnit.PORTS_URL]
                                                if DockerTemplateUnit.PORTS_URL in public_cfg else None)
            binding_docker = PortBinding(name=public_cfg[DockerTemplateUnit.PORTS_NAME],
                                         port_from=public_cfg[DockerTemplateUnit.PORTS_HOST_PORT],
                                         port_to=public_cfg[DockerTemplateUnit.PORTS_PORT],
                                         binding_type=PortBindingType.Docker,
                                         binding_resource_id=host_server.id,
                                         virtual_environment=ve,
                                         experiment=expr)
            binding_dockers.append(binding_docker)
            db_adapter.add_object(binding_cloud_service)
            db_adapter.add_object(binding_docker)
        db_adapter.commit()

        local_ports_cfg = filter(lambda p: DockerTemplateUnit.PORTS_PUBLIC not in p, port_cfg)
        for local_cfg in local_ports_cfg:
            port_binding = PortBinding(name=local_cfg[DockerTemplateUnit.PORTS_NAME],
                                       port_from=local_cfg[DockerTemplateUnit.PORTS_HOST_PORT],
                                       port_to=local_cfg[DockerTemplateUnit.PORTS_PORT],
                                       binding_type=PortBindingType.Docker,
                                       binding_resource_id=host_server.id,
                                       virtual_environment=ve,
                                       experiment=expr)
            binding_dockers.append(port_binding)
            db_adapter.add_object(port_binding)
        db_adapter.commit()
        return binding_dockers

    def __remote_start_container(self, expr, host_server, virtual_environment_dic):
        docker_template_unit = DockerTemplateUnit(virtual_environment_dic)
        old_name = docker_template_unit.get_name()
        suffix = "".join(random.sample(string.ascii_letters + string.digits, 8))
        new_name = '%d-%s-%s' % (expr.id, old_name, suffix)
        docker_template_unit.set_name(new_name)
        log.debug("starting to start container: %s" % new_name)
        # db entity
        ve = VirtualEnvironment(provider=VEProvider.Docker,
                                name=new_name,
                                image=docker_template_unit.get_image(),
                                status=VEStatus.Init,
                                remote_provider=VERemoteProvider.Guacamole,
                                experiment=expr)
        container = DockerContainer(expr,
                                    name=new_name,
                                    host_server=host_server,
                                    virtual_environment=ve,
                                    image=docker_template_unit.get_image())
        db_adapter.add_object(ve)
        db_adapter.add_object(container)
        db_adapter.commit()

        # port binding
        ps = map(lambda p:
                 [p.port_from, p.port_to],
                 self.__assign_ports(expr, host_server, ve, docker_template_unit.get_ports()))

        # guacamole config
        guacamole = docker_template_unit.get_remote()
        port_cfg = filter(lambda p:
                          p[DockerTemplateUnit.PORTS_PORT] == guacamole[DockerTemplateUnit.REMOTE_PORT],
                          docker_template_unit.get_ports())
        if len(port_cfg) > 0:
            gc = {
                "displayname": new_name,
                "name": new_name,
                "protocol": guacamole[DockerTemplateUnit.REMOTE_PROTOCOL],
                "hostname": host_server.public_ip,
                "port": port_cfg[0]["public_port"]
            }
            if DockerTemplateUnit.REMOTE_USERNAME in guacamole:
                gc["username"] = guacamole[DockerTemplateUnit.REMOTE_USERNAME]
            if DockerTemplateUnit.REMOTE_PASSWORD in guacamole:
                gc["password"] = guacamole[DockerTemplateUnit.REMOTE_PASSWORD]
            # save guacamole config into DB
            ve.remote_paras = json.dumps(gc)

        # start container remotely
        container_ret = docker_formation.run(docker_template_unit, host_server)
        if container_ret is None:
            log.error("container %s fail to run" % new_name)
            raise Exception("container_ret is none")
        container.container_id = container_ret["container_id"]
        ve.status = VEStatus.Running
        host_server.container_count += 1
        db_adapter.commit()
        log.debug("starting container %s is ended ... " % new_name)
        return ve

    def __check_expr_status(self, user_id, hackathon, template):
        """
        check experiment status, if there are pre-allocate experiments, the experiment will be assigned directly
        :param user_id:
        :param hackathon:
        :param template:
        :return:
        """
        expr = db_adapter.find_first_object_by(Experiment,
                                               status=EStatus.Running,
                                               user_id=user_id,
                                               hackathon_id=hackathon.id)
        if expr is not None:
            return expr

        expr = db_adapter.find_first_object_by(Experiment,
                                               status=EStatus.Starting,
                                               user_id=user_id,
                                               hackathon_id=hackathon.id)
        if expr is not None:
            return expr

        expr = db_adapter.find_first_object_by(Experiment,
                                               status=EStatus.Running,
                                               hackathon_id=hackathon.id,
                                               user_id=ReservedUser.DefaultUserID,
                                               template=template)
        if expr is not None:
            db_adapter.update_object(expr, user_id=user_id)
            db_adapter.commit()
            log.debug("experiment had been assigned, check experiment and start new job ... ")

            # add a job to start new pre-allocate experiment
            open_check_expr()
            return expr

    def __release_ports(self, expr_id, host_server):
        """
        release the specified experiment's ports
        """
        log.debug("Begin to release ports: expr_id: %d, host_server: %r" % (expr_id, host_server))
        ports_binding = db_adapter.find_all_objects_by(PortBinding, experiment_id=expr_id)
        if ports_binding is not None:
            docker_binding = filter(lambda u: safe_get_config("environment", "prod") != "local" and u.binding_type == 1,
                                    ports_binding)
            ports_to = [d.port_to for d in docker_binding]
            if len(ports_to) != 0:
                self.__release_public_ports(expr_id, host_server, ports_to)
            for port in ports_binding:
                db_adapter.delete_object(port)
            db_adapter.commit()
        log.debug("End to release ports: expr_id: %d, host_server: %r" % (expr_id, host_server))

    def __roll_back(self, expr_id):
        """
        roll back when exception occurred
        :param expr_id: experiment id
        """
        log.debug("Starting rollback ...")
        expr = db_adapter.find_first_object_by(Experiment, id=expr_id)
        try:
            expr.status = EStatus.Rollbacking
            db_adapter.commit()
            if expr is not None:
                # delete containers and change expr status
                for c in expr.virtual_environments:
                    if c.provider == VEProvider.Docker:
                        docker_formation.delete(c.name, c.container.host_server)
                        c.status = VEStatus.Deleted
                        c.container.host_server.container_count -= 1
                        if c.container.host_server.container_count < 0:
                            c.container.host_server.container_count = 0
                        self.__release_ports(expr_id, c.container.host_server)
            # delete ports
            expr.status = EStatus.Rollbacked

            db_adapter.commit()
            log.info("Rollback succeeded")
        except Exception as e:
            expr.status = EStatus.Failed
            db_adapter.commit()
            log.info("Rollback failed")
            log.error(e)

    # --------------------------------------------- helper function ---------------------------------------------#


def open_check_expr():
    """
    start a scheduled job to examine default experiment
    :return:
    """
    log.debug("start checking experiment ... ")
    alarm_time = get_now() + timedelta(seconds=1)
    scheduler.add_job(check_default_expr, 'interval', id='pre', replace_existing=True, next_run_time=alarm_time,
                      minutes=safe_get_config("pre_allocate.check_interval_minutes", 5))


def check_default_expr():
    hackathon_id_list = hack_manager.get_pre_allocate_enabled_hackathoon_list()
    templates = db_adapter.find_all_objects_order(Template, Template.hackathon_id._in(hackathon_id_list))
    for template in templates:
        try:
            pre_num = hack_manager.get_pre_allocate_number(template.hackathon)
            curr_num = db_adapter.count(Experiment,
                                        Experiment.user_id == ReservedUser.DefaultUserID,
                                        Experiment.template_id == template.id,
                                        (Experiment.status == EStatus.Starting) | (
                                            Experiment.status == EStatus.Running))
            # todo test azure, config num
            if template.provider == VEProvider.AzureVM:
                if curr_num < pre_num:
                    remain_num = pre_num - curr_num
                    start_num = db_adapter.count_by(Experiment,
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
                        # log.debug("all template %s start complete" % template.name)
            elif template.provider == VEProvider.Docker:
                log.debug("template name is %s, hackathon name is %s" % (template.name, template.hackathon.name))
                if curr_num < pre_num:
                    remain_num = pre_num - curr_num
                    log.debug("no idle template: %s, remain num is %d ... " % (template.name, remain_num))
                    expr_manager.start_expr(template.hackathon.name, template.name, ReservedUser.DefaultUserID)
                    # curr_num += 1
                    break
                    # log.debug("all template %s start complete" % template.name)
        except Exception as e:
            log.error(e)
            log.error("check default experiment failed")


def recycle_expr_scheduler():
    """
    start a scheduled job to recycle inactive experiment
    :return:
    """
    log.debug("Start recycling inactive user experiment")
    excute_time = get_now() + timedelta(minutes=1)
    scheduler.add_job(recycle_expr, 'interval', id='recycle', replace_existing=True, next_run_time=excute_time,
                      minutes=safe_get_config("recycle.check_idle_interval_minutes", 5))


def recycle_expr():
    """
    recycle experiment when idle more than 5 hours
    :return:
    """
    log.debug("start checking experiment ... ")
    recycle_hours = safe_get_config('recycle.idle_hours', 24)

    expr_time_cond = Experiment.last_heart_beat_time + timedelta(hours=recycle_hours) > get_now()
    recycle_cond = Experiment.hackathon_id._in(hack_manager.get_recyclable_hackathon_list())
    r = db_adapter.find_first_object(Experiment, expr_time_cond, recycle_cond)

    if r is not None:
        expr_manager.stop_expr(r.id)
        log.debug("it's stopping " + str(r.id) + " inactive experiment now")
    else:
        log.debug("There is now inactive experiment now")
        return


expr_manager = ExprManager()
