import sys

sys.path.append("..")

from compiler.ast import flatten
from flask import g
from hackathon.constants import GUACAMOLE
from hackathon.docker import OssDocker
from hackathon.functions import *
from hackathon.enum import *
from hackathon.azureautodeploy.azureImpl import AzureImpl
from hackathon.azureautodeploy.azureUtil import *

docker = OssDocker()
azure = AzureImpl()
sub_id = get_config("azure/subscriptionId")
cert_path = get_config('azure/certPath')
service_host_base = get_config("azure/managementServiceHostBase")
azure.connect(sub_id, cert_path, service_host_base)
uo_id = 0


class ExprManager(object):
    def __report_expr_status(self, expr):
        ret = {
            "expr_id": expr.id,
            "status": expr.status,
            "hackathon": expr.hackathon.name,
            "create_time": str(expr.create_time),
            "last_heart_beat_time": str(expr.last_heart_beat_time),
        }
        guacamole_servers = []
        if expr.user_template.template.provider == VirtualEnvironmentProvider.Docker:
            ves = expr.virtual_environments.all()
        else:
            ves = db_adapter.find_all_objects(VMConfig, user_template_id=expr.user_template.id)
        for ve in ves:
            # return guacamole link to frontend
            if ve.remote_provider == RemoteProvider.Guacamole:
                guaca_config = json.loads(ve.remote_paras)
                url = "%s/guacamole/client.xhtml?id=" % (
                    safe_get_config("guacamole/host", "localhost:8080")) + "c%2F" + str(guaca_config["name"])
                guacamole_servers.append({
                    "name": guaca_config["displayname"],
                    "url": url
                })
        ret["guacamole_servers"] = guacamole_servers
        public_urls = []
        # return public accessible web url
        for ve in expr.virtual_environments.filter(VirtualEnvironment.image != GUACAMOLE.IMAGE).all():
            # todo only docker handled now. add Azure VM support later
            if ve.provider == VirtualEnvironmentProvider.Docker:
                for p in ve.port_bindings.all():
                    if p.binding_type == PortBindingType.CloudService:
                        hs = db_adapter.find_first_object(DockerHostServer, id=p.binding_resource_id)
                        url = "http://%s:%s" % (hs.public_dns, p.port_from)
                        public_urls.append({
                            "name": p.name,
                            "url": url
                        })
        ret["public_urls"] = public_urls
        if expr.user_template.template.provider == VirtualEnvironmentProvider.AzureVM:
            if expr.status == ExprStatus.Starting:
                global uo_id
                uo = query_user_operation(expr.user_template, CREATE, uo_id)
                if len(uo) > 0:
                    uo_last = uo[-1]
                    if uo_last.status == FAIL:
                        expr.status = ExprStatus.Failed
                        db_adapter.commit()
                    if uo_last.operation == CREATE and uo_last.status == END:
                        expr.status = ExprStatus.Running
                        db_adapter.commit()
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

    def __get_available_host_port(self, port_bindings, port):
        host_port = port + 10000

        while len(filter(lambda p: p.port_from == host_port, port_bindings)) > 0:
            host_port += 1

        if host_port >= 65535:
            log.error("port used up on this host server")
            raise Exception("no port available")

        return host_port

    def __assign_port(self, expr, host_server, ve, port_cfg):

        if port_cfg.has_key("public"):
            # todo open port on azure for those must open to public
            # public port means the port open the public. For azure , it's the public port on azure. There
            # should be endpoint on azure that from public_port to host_port
            if not "host_port" in port_cfg:
                port_cfg["host_port"] = port_cfg["port"]
            if not "public_port" in port_cfg:
                port_cfg["public_port"] = port_cfg["host_port"]

            if safe_get_config("environment", "prod") == "local" and port_cfg["host_port"] == 80:
                port_cfg["host_port"] += 10000
                port_cfg["public_port"] = port_cfg["host_port"]

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
            host_ports = db_adapter.find_all_objects(PortBinding, binding_type=PortBindingType.Docker,
                                                     binding_resource_id=host_server.id)
            port_cfg["host_port"] = self.__get_available_host_port(host_ports, port_cfg["port"])

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
                    "hostname": host_server.private_ip,
                    "port": port_cfg[0]["host_port"]
                }
                if "username" in guac:
                    gc["username"] = guac["username"]
                if "password" in guac:
                    gc["password"] = guac["password"]

                # save guacamole config into DB
                ve.remote_paras = json.dumps(gc)

        # start container remotely
        container_ret = docker.run(post_data, host_server.public_dns)
        if container_ret is None:
            log.info("container %s fail to run" % post_data["container_name"])
            raise AssertionError
        container.container_id = container_ret["container_id"]
        ve.status = VirtualEnvStatus.Running
        host_server.container_count += 1
        db_adapter.add_object(ve)
        db_adapter.add_object(container)
        db_adapter.commit()
        return ve

    def get_expr_status(self, expr_id):
        expr = db_adapter.find_first_object(Experiment, id=expr_id)
        if expr is not None:
            return self.__report_expr_status(expr)
        else:
            return "Not found", 404

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
            guacamole_config = []
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
                return "Failed starting containers", 500
        else:
            expr.status = ExprStatus.Starting
            db_adapter.commit()
            # start create azure vm according to user template
            if not azure.create_async(user_template):
                m = 'failed creating azure vm'
                log.error(m)
                return m
        # after everything is ready, set the expr state to running

        # response to caller
        return self.__report_expr_status(expr)

    def heart_beat(self, expr_id):
        expr = Experiment.query.filter_by(id=expr_id, status=ExprStatus.Running).first()
        if expr is None:
            return "Not running", 404

        expr.last_heart_beat_time = datetime.utcnow()
        db_adapter.commit()
        return "OK"

    def __roll_back(self, expr_id):
        log.info("Starting rollback ...")
        expr = Experiment.query.filter_by(id=expr_id).first()
        try:
            expr.status = ExprStatus.Rollbacking
            db_adapter.commit()
            if expr is not None:
                # stop containers and change expr status
                for c in expr.virtual_environments:
                    if c.provider == VirtualEnvironmentProvider.Docker:
                        docker.stop(c.name, c.container.host_server.public_dns)
                        c.status = VirtualEnvStatus.Stopped
                        c.container.host_server.container_count -= 1
                        if c.container.host_server.container_count < 0:
                            c.container.host_server.container_count = 0
            # delete ports
            ports = PortBinding.query.filter_by(experiment_id=expr_id).all()
            for port in ports:
                db.session.delete(port)
            expr.status = ExprStatus.Rollbacked
            db.session.commit()
            log.info("Rollback succeeded")
        except Exception as e:
            expr.status = ExprStatus.Failed
            db.session.commit()
            log.info("Rollback failed")
            log.error(e)

    def stop_expr(self, expr_id):
        expr = db_adapter.find_first_object(Experiment, id=expr_id, status=ExprStatus.Running)
        if expr is not None:
            # Docker
            if expr.user_template.template.provider == VirtualEnvironmentProvider.Docker:
                # stop containers
                for c in expr.virtual_environments:
                    try:
                        docker.stop(c.name, c.container.host_server.public_dns)
                        c.status = VirtualEnvStatus.Stopped
                        c.container.host_server.container_count -= 1
                        if c.container.host_server.container_count < 0:
                            c.container.host_server.container_count = 0
                    except Exception as e:
                        log.error(e)
            else:
                if not azure.shutdown_async(expr.user_template):
                    m = 'failed stopping azure vm'
                    log.error(m)
                    return m
            expr.status = ExprStatus.Stopped
            db_adapter.commit()
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