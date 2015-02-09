import sys

sys.path.append("..")

from compiler.ast import flatten
from flask import g
from hackathon.constants import GUACAMOLE
from hackathon.docker import OssDocker
from hackathon.enum import *
from hackathon.azureautodeploy.azureUtil import *
from hackathon.azureautodeploy.portManagement import *
from hackathon.functions import safe_get_config, get_config, post_to_remote
from subprocess import Popen

docker = OssDocker()


class ExprManager(object):
    def __report_expr_status(self, expr):
        ret = {
            "expr_id": expr.id,
            "status": expr.status,
            "hackathon": expr.hackathon.name,
            "create_time": str(expr.create_time),
            "last_heart_beat_time": str(expr.last_heart_beat_time),
        }

        if expr.status != ExprStatus.Running:
            return ret

        # return guacamole link to frontend
        guacamole_servers = []
        if expr.user_template.template.provider == VirtualEnvironmentProvider.Docker:
            ves = expr.virtual_environments.all()
        else:
            ves = db_adapter.find_all_objects(VMConfig, user_template_id=expr.user_template.id)
        for ve in ves:
            if ve.remote_provider == RemoteProvider.Guacamole:
                guaca_config = json.loads(ve.remote_paras)
                url = "%s/guacamole/client.xhtml?id=" % (
                    safe_get_config("guacamole/host", "localhost:8080")) + "c%2F" + guaca_config["name"]
                guacamole_servers.append({
                    "name": guaca_config["displayname"],
                    "url": url
                })
        if expr.status == ExprStatus.Running:
            ret["remote_servers"] = guacamole_servers

        # return public accessible web url
        public_urls = []
        if expr.user_template.template.provider == VirtualEnvironmentProvider.Docker:
            for ve in expr.virtual_environments.filter(VirtualEnvironment.image != GUACAMOLE.IMAGE).all():
                for p in ve.port_bindings.all():
                    if p.binding_type == PortBindingType.CloudService and p.name == "website":
                        hs = db_adapter.find_first_object(DockerHostServer, id=p.binding_resource_id)
                        url = "http://%s:%s" % (hs.public_dns, p.port_from)
                        public_urls.append({
                            "name": p.name,
                            "url": url
                        })
        else:
            for vm_config in db_adapter.find_all_objects(VMConfig, user_template_id=expr.user_template.id):
                dns = vm_config.dns[:-1]
                vm = vm_config.virtual_machine
                endpoint = db_adapter.find_first_object(VMEndpoint, private_port=80, virtual_machine=vm)
                name = endpoint.name
                port = endpoint.public_port
                public_urls.append({
                    "name": name,
                    "url": dns + ':' + str(port)
                })
        ret["public_urls"] = public_urls

        return ret

    def __get_available_docker_host(self, expr_config):
        req_count = len(expr_config["virtual_environments"])
        vm = db_adapter.filter(DockerHostServer,
                               DockerHostServer.container_count + req_count <= DockerHostServer.container_max_count).first()

        # todo connect to azure to launch new VM if no existed VM meet the requirement
        # since it takes some time to launch VM, it's more reasonable to launch VM when the existed ones are almost used up.
        # The new-created VM must run 'cloudvm service by default(either cloud-init or python remote ssh)
        # todo the VM private IP will change after reboot, need sync the IP in db with azure in this case
        if vm is None:
            raise Exception("No available VM.")
        return vm

    # todo p = PortManagement()
    def __get_available_public_port(self, host_server, host_port):
        p = PortManagement()
        sub_id = get_config("azure/subscriptionId")
        cert_path = get_config('azure/certPath')
        service_host_base = get_config("azure/managementServiceHostBase")
        p.connect(sub_id, cert_path, service_host_base)

        host_server_name = host_server.vm_name
        host_server_dns = host_server.public_dns.split('.')[0]
        public_port = p.assign_public_port(host_server_dns, 'Production', host_server_name, host_port)
        return public_port

    def __release_public_port(self, host_server, host_port):
        p = PortManagement()
        sub_id = get_config("azure/subscriptionId")
        cert_path = get_config('azure/certPath')
        service_host_base = get_config("azure/managementServiceHostBase")
        p.connect(sub_id, cert_path, service_host_base)

        host_server_name = host_server.vm_name
        host_server_dns = host_server.public_dns.split('.')[0]
        p.release_public_port(host_server_dns, 'Production', host_server_name, host_port)

    def __assign_port(self, expr, host_server, ve, port_cfg):

        if port_cfg.has_key("public"):
            # todo open port on azure for those must open to public
            # public port means the port open the public. For azure , it's the public port on azure. There
            # should be endpoint on azure that from public_port to host_port
            # host_ports = db_adapter.find_all_objects(PortBinding, binding_type=PortBindingType.Docker,
            #                                        binding_resource_id=host_server.id)

            if not "host_port" in port_cfg:
                port_cfg["host_port"] = docker.get_available_host_port(host_server, port_cfg["port"])
            if not "public_port" in port_cfg:
                if safe_get_config("environment", "prod") == "local":
                    port_cfg["public_port"] = port_cfg["host_port"]
                else:
                    port_cfg["public_port"] = self.__get_available_public_port(host_server, port_cfg["host_port"])

            binding_cloudservice = PortBinding(name=port_cfg["name"] if "name" in port_cfg else None,
                                               port_from=port_cfg["public_port"],
                                               port_to=port_cfg["host_port"],
                                               binding_type=PortBindingType.CloudService,
                                               binding_resource_id=host_server.id,
                                               virtual_environment=ve,
                                               experiment=expr)
            binding_docker = PortBinding(name=port_cfg["name"] if "name" in port_cfg else None,
                                         port_from=port_cfg["host_port"],
                                         port_to=port_cfg["port"],
                                         binding_type=PortBindingType.Docker,
                                         binding_resource_id=host_server.id,
                                         virtual_environment=ve,
                                         experiment=expr)
            db_adapter.add_object(binding_cloudservice)
            db_adapter.add_object(binding_docker)
            db_adapter.commit()
            return binding_docker
        else:
            port_cfg["host_port"] = docker.get_available_host_port(host_server, port_cfg["port"])

            port_binding = PortBinding(name=port_cfg["name"] if "name" in port_cfg else None,
                                       port_from=port_cfg["host_port"],
                                       port_to=port_cfg["port"],
                                       binding_type=PortBindingType.Docker,
                                       binding_resource_id=host_server.id,
                                       virtual_environment=ve,
                                       experiment=expr)
            db_adapter.add_object(port_binding)
            db_adapter.commit()
            return port_binding

    def __get_cloudvm_address(self, host_server):
        # the port is that cloudvm service is listening on. By default: 8001 on cloudService and python cmd, 80 on apache2
        # connect to cloudvm service through its private address when deploy on azure. Here its public address used for
        # debug purpose since local dev environment cannot access its private address
        return "http://%s:%s" % (host_server.public_dns, 8001)
        # return "%s:%s" % (host_server.private_ip, host_server.private_cloudvm_port)

    def __remote_checkout(self, host_server, expr, scm):
        post_data = scm
        post_data["expr_id"] = expr.id

        url = "%s/scm" % self.__get_cloudvm_address(host_server)
        return post_to_remote(url, post_data)

    def __remote_start_container(self, expr, host_server, scm, container_config):
        post_data = container_config
        post_data["expr_id"] = expr.id
        post_data["container_name"] = "%s-%s" % (expr.id, container_config["name"])

        # db entity
        provider = container_config["provider"] if "provider" in container_config else VirtualEnvironmentProvider.Docker
        remote_provider = ""
        if "remote" in post_data and "provider" in post_data["remote"]:
            remote_provider = post_data["remote"]["provider"]
        ve = VirtualEnvironment(provider=provider,
                                name=post_data["container_name"],
                                image=container_config["image"],
                                status=VirtualEnvStatus.Init,
                                remote_provider=remote_provider,
                                user=g.user,
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
            ps = map(lambda p: [self.__assign_port(expr, host_server, ve, p).port_from, p["port"]],
                     container_config["ports"])
            container_config["docker_ports"] = flatten(ps)
        if container_config.has_key("mnt"):
            local_repo_path = "" if scm is None else scm["local_repo_path"]
            mnts_with_repo = map(lambda s: s if "%s" not in s else s % local_repo_path, container_config["mnt"])
            container_config["mnt"] = mnts_with_repo

        # add to guacamole config
        # note the port should get from the container["port"] to get corresponding listening port rather than the
        # expose port that defined in the template. Following codes are just example
        if "remote" in container_config and container_config["remote"][
            "provider"] == "guacamole" and "ports" in container_config:
            guac = container_config["remote"]
            port_cfg = filter(lambda p: p["port"] == guac["port"], container_config["ports"])

            if len(port_cfg) > 0:
                gc = {
                    "displayname": port_cfg[0]["name"] if "name" in port_cfg[0] else container_config["name"],
                    "name": post_data["container_name"],
                    "protocol": guac["protocol"],
                    "hostname": host_server.public_dns,
                    "port": port_cfg[0]["public_port"]
                }
                if "username" in guac:
                    gc["username"] = guac["username"]
                if "password" in guac:
                    gc["password"] = guac["password"]

                # save guacamole config into DB
                ve.remote_paras = json.dumps(gc)

        # start container remotely
        container_ret = docker.run(post_data, host_server)
        if container_ret is None:
            log.error("container %s fail to run" % post_data["container_name"])
            raise Exception("container_ret is none")
        container.container_id = container_ret["container_id"]
        ve.status = VirtualEnvStatus.Running
        host_server.container_count += 1
        db_adapter.commit()
        return ve

    def get_expr_status(self, expr_id):
        expr = db_adapter.find_first_object(Experiment, id=expr_id)
        if expr is not None:
            return self.__report_expr_status(expr)
        else:
            return {"error": "Experiment Not found"}, 404

    def start_expr(self, hackathon_name, template_name):
        hackathon = db_adapter.find_first_object(Hackathon, name=hackathon_name)
        if hackathon is None:
            raise Exception("hackathon %s doesn't exist.")

        template = db_adapter.find_first_object(Template, hackathon=hackathon, name=template_name)
        if template is None or not os.path.isfile(template.url):
            raise Exception("template %s doesn't exist.")

        try:
            expr_config = json.load(file(template.url))
        except Exception as e:
            raise Exception(e)

        expr = db_adapter.find_first_object(Experiment,
                                            status=ExprStatus.Running,
                                            user_id=g.user.id,
                                            hackathon_id=hackathon.id)
        if expr is not None:
            return self.__report_expr_status(expr)

        expr = db_adapter.find_first_object(Experiment,
                                            status=ExprStatus.Starting,
                                            user_id=g.user.id,
                                            hackathon_id=hackathon.id)
        if expr is not None:
            return self.__report_expr_status(expr)

        user_template = db_adapter.find_first_object(UserTemplate, user=g.user, template=template)
        if user_template is None:
            user_template = db_adapter.add_object_kwargs(UserTemplate, user=g.user, template=template)
        # new expr
        expr = db_adapter.add_object_kwargs(Experiment,
                                            user=g.user,
                                            hackathon=hackathon,
                                            status=ExprStatus.Init,
                                            user_template=user_template)
        db_adapter.commit()

        if template.provider == VirtualEnvironmentProvider.Docker:
            # get available VM that runs the cloudvm and is available for more containers
            host_server = self.__get_available_docker_host(expr_config)
            # checkout source code
            scm = None
            if "scm" in expr_config:
                s = expr_config["scm"]
                local_repo_path = self.__remote_checkout(host_server, expr, expr_config["scm"])
                scm = db_adapter.add_object_kwargs(SCM,
                                                   experiment=expr,
                                                   provider=s["provider"],
                                                   branch=s["branch"],
                                                   repo_name=s["repo_name"],
                                                   repo_url=s["repo_url"],
                                                   local_repo_path=local_repo_path)
                db_adapter.commit()
            # start containers
            # guacamole_config = []
            try:
                expr.status = ExprStatus.Starting
                db_adapter.commit()
                map(lambda container_config:
                    self.__remote_start_container(expr, host_server, scm, container_config),
                    expr_config["virtual_environments"])
                expr.status = ExprStatus.Running
                db_adapter.commit()
            except Exception as e:
                log.error(e)
                log.error("Failed starting containers")
                self.__roll_back(expr.id)
                return {"error": "Failed starting containers"}, 500
        else:
            expr.status = ExprStatus.Starting
            db_adapter.commit()
            # start create azure vm according to user template
            try:
                path = os.path.dirname(__file__) + '/../azureautodeploy/azureCreateAsync.py'
                command = ['python', path, str(user_template.id), str(expr.id)]
                Popen(command)
            except Exception as e:
                log.error(e)
                return {"error": "Failed starting azure"}, 500
        # after everything is ready, set the expr state to running

        # response to caller
        return self.__report_expr_status(expr)

    def heart_beat(self, expr_id):
        expr = Experiment.query.filter_by(id=expr_id, status=ExprStatus.Running).first()
        if expr is None:
            return {"error": "Experiment doesn't running"}, 404

        expr.last_heart_beat_time = datetime.utcnow()
        db_adapter.commit()
        return "OK"

    def __release_ports(self, expr_id, host_server):
        ports = PortBinding.query.filter_by(experiment_id=expr_id).all()
        if ports is not None:
            for port in ports:
                if port.binding_type == 1:
                    self.__release_public_port(host_server, port.port_to)
                db.session.delete(port)
            db.session.commit()

    def __roll_back(self, expr_id):
        """
        force delete container

        :param expr_id: experiment id
        """
        log.info("Starting rollback ...")
        expr = Experiment.query.filter_by(id=expr_id).first()
        try:
            expr.status = ExprStatus.Rollbacking
            db_adapter.commit()
            if expr is not None:
                # delete containers and change expr status
                for c in expr.virtual_environments:
                    if c.provider == VirtualEnvironmentProvider.Docker:
                        docker.delete(c.name, c.container.host_server)
                        c.status = VirtualEnvStatus.Deleted
                        c.container.host_server.container_count -= 1
                        if c.container.host_server.container_count < 0:
                            c.container.host_server.container_count = 0
                        self.__release_ports(expr_id, c.container.host_server)
            # delete ports
            expr.status = ExprStatus.Rollbacked
            db.session.commit()
            log.info("Rollback succeeded")
        except Exception as e:
            expr.status = ExprStatus.Failed
            db.session.commit()
            log.info("Rollback failed")
            log.error(e)

    def stop_expr(self, expr_id, force=0):
        """
        :param expr_id: experiment id
        :param force: 0: only stop container and release ports, 1: force stop and delete container and release ports.
        :return:
        """
        expr = db_adapter.find_first_object(Experiment, id=expr_id, status=ExprStatus.Running)
        if expr is not None:
            # Docker
            if expr.user_template.template.provider == VirtualEnvironmentProvider.Docker:
                # stop containers
                for c in expr.virtual_environments:
                    try:
                        if force:
                            docker.delete(c.name, c.container.host_server)
                            c.status = VirtualEnvStatus.Deleted
                        else:
                            docker.stop(c.name, c.container.host_server)
                            c.status = VirtualEnvStatus.Stopped
                        c.container.host_server.container_count -= 1
                        if c.container.host_server.container_count < 0:
                            c.container.host_server.container_count = 0
                        self.__release_ports(expr_id, c.container.host_server)
                    except Exception as e:
                        log.error(e)
                        return {"error": "Failed stop/delete container"}, 500
                if force:
                    expr.status = ExprStatus.Deleted
                else:
                    expr.status = ExprStatus.Stopped
                db_adapter.commit()
            else:
                try:
                    path = os.path.dirname(__file__) + '/../azureautodeploy/azureShutdownAsync.py'
                    command = ['python', path, str(expr.user_template.id), str(expr.id)]
                    Popen(command)
                except Exception as e:
                    log.error(e)
                    return {"error": "Failed shutdown azure"}, 500
            return "OK"
        else:
            return "expr not exist"

    def submit_expr(self, args):
        if "id" not in args:
            log.warn("cannot submit expr for the lack of id")
            raise Exception("id unavailable")

        id = args["id"]
        u = db_adapter.find_first_object(Register, id=id)
        if u is None:
            log.debug("register user not found:" + id)
            return "user not found", 404

        # u.online = args["online"] if "online" in args else u.online
        u.submitted = args["submitted"] if "submitted" in args else u.submitted
        u.submitted_time = datetime.utcnow()
        db_adapter.commit()
        return u


expr_manager = ExprManager()