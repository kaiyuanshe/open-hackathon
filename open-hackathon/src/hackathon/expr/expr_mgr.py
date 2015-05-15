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

from compiler.ast import (
    flatten,
)
from hackathon.dockerformation.dockerFormation import (
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
    RecycleStatus,
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
    datetime,
)
from hackathon.hackathon_response import (
    internal_server_error,
    precondition_failed,
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

        expr_config = json.load(file(template.url))

        curr_num = db_adapter.count(Experiment, Experiment.user_id == ReservedUser.DefaultUserID,
                                    Experiment.template == template,
                                    (Experiment.status == EStatus.Starting) | (
                                        Experiment.status == EStatus.Running))
        if template.provider == VEProvider.Docker:
            # get available VM that runs the cloudvm and is available for more containers
            # start containers
            # guacamole_config = []
            try:
                host_server = self.__get_available_docker_host(expr_config, hackathon)
                if curr_num != 0 and curr_num >= get_config("pre_allocate.docker"):
                    return
                expr.status = EStatus.Starting
                db_adapter.commit()
                map(lambda container_config:
                    self.__remote_start_container(expr, host_server, container_config, user_id),
                    expr_config["virtual_environments"])
                expr.status = EStatus.Running
                db_adapter.commit()
            except Exception as e:
                log.error(e)
                log.error("Failed starting containers")
                self.__roll_back(expr.id)
                return {"error": "Failed starting containers"}, 500
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
                return {"error": "Failed starting azure"}, 500
        # after everything is ready, set the expr state to running
        # response to caller
        return self.__report_expr_status(expr)

    def heart_beat(self, expr_id):
        expr = db_adapter.find_first_object_by(Experiment, id=expr_id, status=EStatus.Running)
        if expr is None:
            return {"error": "Experiment doesn't running"}, 404

        expr.last_heart_beat_time = datetime.utcnow()
        db_adapter.commit()
        return "OK"

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
                        return {"error": "Failed stop/delete container"}, 500
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
                    return {'error': 'Failed stopping azure'}, 500

            log.debug("experiment %d ended success" % expr_id)
            return "OK"
        else:
            return "expr not exist"

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
                url = guacamole_host + '/guacamole/#/client/c%s?name=%s' % (name, name)
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
                        url = p.url % (hs.public_dns, p.port_from)
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

    def __get_available_docker_host(self, expr_config, hackathon):
        req_count = len(expr_config["virtual_environments"])

        vm = db_adapter.find_first_object(DockerHostServer,
                                          DockerHostServer.container_count + req_count <= DockerHostServer.container_max_count,
                                          DockerHostServer.hackathon_id == hackathon.id)


        # todo connect to azure to launch new VM if no existed VM meet the requirement
        # since it takes some time to launch VM, it's more reasonable to launch VM when the existed ones are almost used up.
        # The new-created VM must run 'cloudvm service by default(either cloud-init or python remote ssh)
        # todo the VM private IP will change after reboot, need sync the IP in db with azure in this case
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
            return "cannot get public ports", 500
        for ep in public_endpoints:
            log.debug("public port : %d" % ep)
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
        """
        # get 'host_port'
        map(lambda p: p.update(
            {'host_port': docker_formation.get_available_host_port(host_server, p['port'])}) if 'host_port' not in p else None,
            port_cfg)

        # get 'public' cfg
        public_ports_cfg = filter(lambda p: 'public' in p, port_cfg)
        host_ports = [u['host_port'] for u in public_ports_cfg]
        if safe_get_config("environment", "prod") == "local":
            map(lambda cfg: cfg.update({'public_port': cfg['host_port']}), public_ports_cfg)
        else:
            # todo is __get_available_public_port args is list
            public_ports = self.__get_available_public_ports(expr.id, host_server, host_ports)
            # public_ports = [self.__get_available_public_port(host_server, port) for port in host_ports]
            for i in range(len(public_ports_cfg)):
                public_ports_cfg[i]['public_port'] = public_ports[i]

        binding_dockers = []

        # update portbinding
        for public_cfg in public_ports_cfg:
            binding_cloud_service = PortBinding(name=public_cfg["name"] if "name" in public_cfg else None,
                                                port_from=public_cfg["public_port"],
                                                port_to=public_cfg["host_port"],
                                                binding_type=PortBindingType.CloudService,
                                                binding_resource_id=host_server.id,
                                                virtual_environment=ve,
                                                experiment=expr)
            binding_docker = PortBinding(name=public_cfg["name"] if "name" in public_cfg else None,
                                         port_from=public_cfg["host_port"],
                                         port_to=public_cfg["port"],
                                         binding_type=PortBindingType.Docker,
                                         binding_resource_id=host_server.id,
                                         virtual_environment=ve,
                                         experiment=expr)
            binding_dockers.append(binding_docker)
            db_adapter.add_object(binding_cloud_service)
            db_adapter.add_object(binding_docker)
        db_adapter.commit()

        local_ports_cfg = filter(lambda p: 'public' not in p, port_cfg)
        for local_cfg in local_ports_cfg:
            port_binding = PortBinding(name=local_cfg["name"] if "name" in local_cfg else None,
                                       port_from=local_cfg["host_port"],
                                       port_to=local_cfg["port"],
                                       binding_type=PortBindingType.Docker,
                                       binding_resource_id=host_server.id,
                                       virtual_environment=ve,
                                       experiment=expr)
            binding_dockers.append(port_binding)
            db_adapter.add_object(port_binding)
        db_adapter.commit()
        return binding_dockers

    def __remote_start_container(self, expr, host_server, container_config, user_id):
        post_data = container_config
        post_data["expr_id"] = expr.id
        post_data["container_name"] = "%s-%s" % (expr.id, container_config["name"]) + "".join(random.sample(string.ascii_letters + string.digits, 8))
        log.debug("starting to start container: %s" % post_data["container_name"])

        # db entity
        provider = VEProvider.Docker
        remote_provider = VERemoteProvider.Guacamole
        # user = g.get('user', None)
        ve = VirtualEnvironment(provider=provider,
                                name=post_data["container_name"],
                                image=container_config["image"],
                                status=VEStatus.Init,
                                remote_provider=remote_provider,
                                experiment=expr)
        container = DockerContainer(expr, name=post_data["container_name"], host_server=host_server,
                                    virtual_environment=ve,
                                    image=container_config["image"])

        db_adapter.add_object(ve)
        db_adapter.add_object(container)
        db_adapter.commit()
        # format data in the template such as port and mnt.
        # the port defined in template have only expose port, we should assign a listening port in program
        # the mnt may contain placeholder for source code dir which are decided by 'cloudvm' service
        if "ports" in container_config:
            # get an available on the target VM

            # ps = map(lambda p: [self.__assign_port(expr, host_server, ve, p).port_from, p["port"]],
            # container_config["ports"])

            ps = map(lambda p: [p.port_from, p.port_to],
                     self.__assign_ports(expr, host_server, ve, container_config["ports"]))

            container_config["docker_ports"] = flatten(ps)
        # add to guacamole config
        # note the port should get from the container["port"] to get corresponding listening port rather than the
        # expose port that defined in the template. Following codes are just example
        if "remote" in container_config \
                and container_config["remote"]["provider"] == "guacamole" \
                and "ports" in container_config:
            guacamole = container_config["remote"]
            port_cfg = filter(lambda p: p["port"] == guacamole["port"], container_config["ports"])

            if len(port_cfg) > 0:
                gc = {
                    "displayname": container_config["displayname"] if "displayname" in container_config else
                    container_config["name"],
                    "name": post_data["container_name"],
                    "protocol": guacamole["protocol"],
                    "hostname": host_server.public_ip,
                    "port": port_cfg[0]["public_port"]
                }
                if "username" in guacamole:
                    gc["username"] = guacamole["username"]
                if "password" in guacamole:
                    gc["password"] = guacamole["password"]

                # save guacamole config into DB
                ve.remote_paras = json.dumps(gc)

        # start container remotely
        container_ret = docker_formation.run(post_data, host_server)
        if container_ret is None:
            log.error("container %s fail to run" % post_data["container_name"])
            raise Exception("container_ret is none")
        container.container_id = container_ret["container_id"]
        ve.status = VEStatus.Running
        host_server.container_count += 1
        db_adapter.commit()
        log.debug("starting container %s is ended ... " % post_data["container_name"])
        return ve

    def __get_expr_status(self, expr_id):
        expr = db_adapter.find_first_object_by(Experiment, id=expr_id)
        if expr is not None:
            return self.__report_expr_status(expr)
        else:
            return {"error": "Experiment Not found"}, 404

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
            for ve in expr.virtual_environments:
                db_adapter.update_object(ve, user_id=user_id)
            db_adapter.commit()
            log.debug("experiment had been assigned, check experiment and start new job ... ")

            # add a job to start new pre-allocate experiment
            alarm_time = datetime.now() + timedelta(seconds=1)
            scheduler.add_job(check_default_expr, 'date', next_run_time=alarm_time)
            return expr

        return None

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
    alarm_time = datetime.now() + timedelta(seconds=1)
    scheduler.add_job(check_default_expr, 'interval', id='1', replace_existing=True, next_run_time=alarm_time,
                      minutes=safe_get_config("pre_allocate.check_interval_minutes", 5))


def check_default_expr():
    # todo only pre-allocate env for those needed. It should configured in table hackathon
    templates = db_adapter.find_all_objects_order_by(Template, hackathon_id=2)
    total_azure = safe_get_config("pre_allocate.azure", 1)
    total_docker = safe_get_config("pre_allocate.docker", 1)
    for template in templates:
        try:
            curr_num = db_adapter.count(Experiment,
                                        Experiment.user_id == ReservedUser.DefaultUserID,
                                        Experiment.template_id == template.id,
                                        (Experiment.status == EStatus.Starting) | (
                                            Experiment.status == EStatus.Running))
            # todo test azure, config num
            if template.provider == VEProvider.AzureVM:
                if curr_num < total_azure:
                    remain_num = total_azure - curr_num
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
                if curr_num < total_docker:
                    remain_num = total_docker - curr_num
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
    excute_time = datetime.utcnow() + timedelta(minutes=1)
    scheduler.add_job(recycle_expr, 'interval', id='2', replace_existing=True, next_run_time=excute_time,
                      minutes=safe_get_config("recycle.check_idle_interval_minutes", 5))


def recycle_expr():
    """
    recycle experiment when idle more than 5 hours
    :return:
    """
    log.debug("start checking experiment ... ")
    recycle_hours = safe_get_config('recycle.idle_hours', 24)
    expr_time_cond = Experiment.last_heart_beat_time + timedelta(hours=recycle_hours) > datetime.utcnow()
    expr_enable_cond = Hackathon.recycle_enabled == RecycleStatus.Enabled
    r = Experiment.query.join(Hackathon).filter(expr_time_cond, expr_enable_cond).first()
    if r is not None:
        expr_manager.stop_expr(r.id)
        log.debug("it's stopping " + str(r.id) + " inactive experiment now")
    else:
        log.debug("There is now inactive experiment now")
        return


expr_manager = ExprManager()
