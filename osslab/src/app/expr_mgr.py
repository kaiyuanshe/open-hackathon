import json
from functions import *
from flask import g
from compiler.ast import flatten
from database import *
from log import log
from constants import *
from registration import Registration

class ExprManager(object):

    def __get_guacamole_container(self, expr):
        return expr.containers.filter_by(image=GUACAMOLE_IMAGE).first()

    def __report_expr_status(self, expr):
        ret = {
            "expr_id": expr.id,
            "type": expr.type,
            "expr_name": expr.expr_name,
            "create_time": str(expr.create_time),
            "last_heart_beat_time": str(expr.last_heart_beat_time),
            "guacamole_status": False
        }

        # fill the status of guacamole container
        guaca_container = self.__get_guacamole_container(expr)
        if guaca_container is not None:
            try:
                guaca_port = guaca_container.port_bindings.filter_by(container_port=GUACAMOLE_PORT).first()
                get_remote("http://%s:%s" % (guaca_container.host_server.public_dns, guaca_port.vm_public_port))
                ret["guacamole_status"] = True
            except Exception as e:
                log.error(e)

            guacamole_servers = []
            for c in expr.containers.all():
                # return guacamole link to frontend
                if c.guacamole is not None:
                    guaca_config = json.loads(c.guacamole)
                    host_server = guaca_container.host_server
                    guaca_pub_port = guaca_container.port_bindings.first().vm_public_port
                    url= "http://%s:%s/client.xhtml?id=" % (host_server.public_dns, guaca_pub_port) + "c%2F" + guaca_config["name"]
                    guacamole_servers.append({
                        "name": guaca_config["name"],
                        "url": url
                    })

            ret["guacamole_servers"] = guacamole_servers

        public_urls = []
        # return public accessible web url
        for c in expr.containers.filter(DockerContainer.image != GUACAMOLE_IMAGE):
            for p in c.port_bindings:
                if p.vm_public_port is not None:
                    url= "http://%s:%s" % (c.host_server.public_dns, p.vm_public_port)
                    public_urls.append({
                        "name": p.name,
                        "url": url
                    })
        ret["public_urls"] = public_urls

        return ret

    def __get_available_vm(self, expr_config):
        req_count= len(expr_config["containers"]) + 1
        vm= HostServer.query.filter(HostServer.container_count + req_count <= HostServer.container_max_count).first()

        # todo connect to azure to launch new VM if no existed VM meet the requirement
        # since it takes some time to launch VM, it's more reasonable to launch VM when the existed ones are almost used up.
        # The new-created VM must run 'cloudvm service by default(either cloud-init or python remote ssh)
        # todo the VM private IP will change after reboot, need sync the IP in db with azure in this case
        if vm is None:
            raise Exception("No available VM.")
        return vm

    def __get_available_host_port(self, port_bindings, port):

        host_port = port + 10000

        while len(filter(lambda p: p.vm_private_port == host_port, port_bindings)) > 0:
            host_port += 1

        if host_port >= 65535:
            log.error("port used up on this host server")
            raise Exception("no port available")

        return host_port

    def __assign_port(self, expr, host_server, container, port_cfg):
        # todo login here is specially for 12/17 hackathon.
        # The right solution is to pick an assign an unused port, open it on cloud service if it's public

        if port_cfg.has_key("public"):
            # todo only registered user can use public port since public ports are limited and manually maintained
            # but it's temporary. remove it after this hackathon
            reg = Registration().get_by_email(expr.user.email)
            if reg is None:
                log.warn("UnRegistered user found. It shouldn't happen!")
                raise Exception("UnRegistered user")

            # todo open port on azure for those must open to public
            # public port means the port open the public. For azure , it's the public port on azure. There
            # should be endpoint on azure that from public_port to host_port
            if not "host_port" in port_cfg:
                port_cfg["host_port"] = port_cfg["port"]
            if not "public_port" in port_cfg:
                port_cfg["public_port"] = port_cfg["host_port"]

            if safe_get_config("environment", "prod") == "local" and port_cfg["host_port"]==80:
                port_cfg["host_port"] += 10000
                port_cfg["public_port"] = port_cfg["host_port"]
        else:
            port_cfg["host_port"] = self.__get_available_host_port(host_server.port_bindings.all(), port_cfg["port"])

        port_binding = PortBinding(port_cfg["name"] if "name" in port_cfg else None,
                                   port_cfg["public_port"] if "public_port" in port_cfg else None,
                                   port_cfg["host_port"],
                                   port_cfg["port"],
                                   host_server,
                                   expr,
                                   container)
        db.session.add(port_binding)
        db.session.commit()

        return port_binding

    def __get_cloudvm_address(self, host_server):
        # the port is that cloudvm service is listening on. By default: 8001 on cloudService and python cmd, 80 on apache2

        # connect to cloudvm service through its private address when deploy on azure. Here its public address used for
        # debug purpose since local dev environment cannot access its private address
        return "http://%s:%s" % (host_server.public_dns, host_server.public_cloudvm_port)
        # return "%s:%s" % (host_server.private_ip, host_server.private_cloudvm_port)

    def __remote_checkout(self, host_server, expr, scm):
        post_data = scm
        post_data["expr_id"] = expr.id

        url= "%s/scm" % self.__get_cloudvm_address(host_server)
        return post_to_remote(url, post_data)

    def __remote_start_container(self, expr, host_server, scm, container_config, guacamole_config):
        post_data = container_config
        post_data["expr_id"] = expr.id
        post_data["container_name"] = "%s-%s" % (expr.id, container_config["name"])

        # db entity
        container = DockerContainer(post_data["container_name"], g.user, host_server, expr, container_config["image"])
        db.session.add(container)
        db.session.commit()

        # format data in the template such as port and mnt.
        # the port defined in template have only expose port, we should assign a listening port in program
        # the mnt may contain placeholder for source code dir which are decided by 'cloudvm' service
        if "ports" in container_config:
            # get an available on the target VM
            ps= map(lambda p: [self.__assign_port(expr, host_server, container, p).vm_private_port, p["port"]],
                    container_config["ports"])
            container_config["docker_ports"] = flatten(ps)
        if container_config.has_key("mnt"):
            local_repo_path = "" if scm is None else scm["local_repo_path"]
            mnts_with_repo = map(lambda s: s if "%s" not in s else s % local_repo_path, container_config["mnt"])
            container_config["mnt"]= mnts_with_repo

        # add to guacamole config
        # note the port should get from the container["port"] to get corresponding listening port rather than the
        # expose port that defined in the template. Following codes are just example
        if "guacamole" in container_config and "ports" in container_config:
            guac = container_config["guacamole"]
            port_cfg = filter(lambda p: p["port"] == guac["port"], container_config["ports"])

            if len(port_cfg) > 0:
                gc = {
                    "name": port_cfg[0]["name"] if "name" in port_cfg[0] else container_config["name"],
                    "protocol": guac["protocol"],
                    "hostname": host_server.private_ip,
                    "port": port_cfg[0]["host_port"]
                }
                if "username" in guac:
                    gc["username"] = guac["username"]
                if "password" in guac:
                    gc["password"] = guac["password"]

                # save guacamole config into DB
                container.guacamole = json.dumps(gc)
                guacamole_config.append(gc)

        # start container remotely
        url = "%s/docker" % self.__get_cloudvm_address(host_server)
        container_ret = post_to_remote(url, post_data)
        container.container_id = container_ret["container_id"]
        container.status = 1
        host_server.container_count += 1
        db.session.commit()

        return container


    def get_expr_status(self, expr_id):
        expr = Experiment.query.filter_by(id=expr_id, status=1).first()
        if expr is not None:
            return self.__report_expr_status(expr)
        else:
            return "Not found", 404

    def start_expr(self, expr_config):
        expr = Experiment.query.filter_by(status=1, user_id=g.user.id).first()
        if expr is not None:
            return self.__report_expr_status(expr)

        # new expr
        expr = Experiment(g.user, "real-time-analytics-hackathon", 0, "docker", expr_config["expr_name"])
        db.session.add(expr)
        db.session.commit()

        # get available VM that runs the cloudvm and is available for more containers
        host_server = self.__get_available_vm(expr_config)

        # checkout source code
        scm = None
        if "scm" in expr_config:
            s = expr_config["scm"]
            local_repo_path = self.__remote_checkout(host_server, expr, expr_config["scm"])
            scm = SCM(expr, s["provider"], s["branch"], s["repo_name"], s["repo_url"], local_repo_path)
            db.session.add(scm)
            db.session.commit()

        # start containers
        guacamole_config = []
        containers = map(lambda container_config: self.__remote_start_container(expr,
                                                                                host_server,
                                                                                scm,
                                                                                container_config,
                                                                                guacamole_config),
                         expr_config["containers"])

        # start guacamole
        if len(guacamole_config) > 0:
            # also, the guacamole port should come from DB
            guacamole_container_config= {
                "name": "guacamole",
                "expr_id": expr.id,
                "image": GUACAMOLE_IMAGE,
                "ports": [{
                    "name": "guacamole",
                    "port": GUACAMOLE_PORT,
                    "public": True
                }],
                "detach": True,
                "guacamole_config": guacamole_config
            }

            guca_container = self.__remote_start_container(expr, host_server, scm, guacamole_container_config, [])
            containers.append(guca_container)

        # after everything is ready, set the expr state to running
        expr.status = 1
        db.session.commit()

        # response to caller
        return self.__report_expr_status(expr)

    def heart_beat(self, expr_id):
        expr = Experiment.query.filter_by(id=expr_id, status=1).first()
        if expr is None:
            return "Not running", 404

        expr.last_heart_beat_time = datetime.utcnow()
        db.session.commit()
        return "OK"

    def stop_expr(self, expr_id):
        expr = Experiment.query.filter_by(id=expr_id, status=1).first()
        if expr is not None:
            # todo delete source code folder to prevent disk from being used up

            # stop containers
            for c in expr.containers:
                try:
                    url = "%s/docker?cname=%s" % (self.__get_cloudvm_address(c.host_server), c.name)
                    delete_remote(url)
                    c.status = 2
                    c.host_server.container_count -= 1
                    if c.host_server.container_count < 0:
                        c.host_server.container_count = 0
                    db.session.commit()
                except Exception as e:
                    log.error(e)

            expr.status = 2
            db.session.commit()

        return "OK"
