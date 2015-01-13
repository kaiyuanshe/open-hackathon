__author__ = 'junbo'

import json

import requests

import log

from database import *

remote_port = "4243"


def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def name_match(id, l):
    for n in l:
        if id in n:
            return True

    return False


class RemoteDocker(object):
    def __init__(self):
        self.headers = {'content-type': 'application/json'}

    def get_vm_url(self, vm_dns):
        # vm = HostServer.query.filter(HostServer.container_count + req_count <= HostServer.container_max_count).first()
        vm_url = "http://" + vm_dns + ":" + remote_port
        return vm_url

    def containers_info(self, vm_dns):
        try:
            containers_url = self.get_vm_url(vm_dns) + "/containers/json"
            req = requests.get(containers_url)
            return convert(json.loads(req.content))
        except Exception as e:
            log.error(e)
            raise AssertionError("cannot get containers' info")

    def get_container(self, name, vm_dns):
        containers = self.containers_info(vm_dns)
        return next((c for c in containers if name in c["Names"] or '/' + name in c["Names"]), None)

    def search_containers_by_expr_id(self, id, vm_dns, all=False):
        get_containers = self.containers_info(vm_dns)
        if all:
            return get_containers
        return filter(lambda c: name_match(id, c["Names"]), get_containers)

    # stop a container, name is the container's name, vm_dns is vm's ip address
    def stop(self, name, vm_dns):
        if self.get_container(name, vm_dns) is not None:
            try:
                containers_url = self.get_vm_url(vm_dns) + "/containers/%s/stop" % name
                requests.post(containers_url)
            except Exception as e:
                log.error(e)
                log.error("container %s fail to stop" % name)
                return False
        return True

    # start a container, vm_dns is vm's ip address, start_config is the configure of container which you want to start
    def start(self, vm_url, container_id, start_config={}):
        url = vm_url + "/containers/%s/start" % container_id
        requests.post(url, data=json.dumps(start_config), headers=self.headers)
        #return self.inspect(vm_dns, container_id)

    # remove a container
    def remove(self, vm_url, container_id):
        url = vm_url + "/containers/%s" % container_id
        requests.delete(url)

    # create a container
    def create(self, vm_url, container_config, container_name):
        containers_url = vm_url + "/containers/create?name=%s" % container_name
        req_create = requests.post(containers_url, data=json.dumps(container_config), headers=self.headers)
        return json.loads(req_create.content)

    # run a container, the configure of container which you want to create, vm_dns is vm's ip address
    def run(self, args, vm_dns):
        container_name = args["container_name"]
        exist = self.get_container(container_name, vm_dns)
        vm_url = self.get_vm_url(vm_dns)
        result = {
            "container_name": container_name
        }
        if exist is not None:
            result["container_id"] = exist["Id"]
        else:
            image = args["image"]
            # ports foramt: [from, to ,from2, to2]. e.g.[9080,8080,3306,3306].Similar with 'mnts'
            ports = args["docker_ports"] if args.has_key("docker_ports") else []
            port_bingings = dict(zip(ports[1::2], ports[::2]))

            mnts = args["mnt"] if args.has_key("mnt") else []
            mnts_f = map(
                lambda s: s if "%s" not in s or not args.has_key("scm") else s % args["scm"]["local_repo_path"],
                mnts[::2])
            mnts_t = map(lambda s: {"bind": s, "ro": False}, mnts[1::2])
            mnt_bindings = dict(zip(mnts_f, mnts_t))
            command = args["command"] if args.has_key('command') else None
            stdin_open = args["stdin_open"] if args.has_key("stdin_open") else False
            tty = args["tty"] if args.has_key("tty") else False
            dns = args["dns"] if args.has_key("dns") else None
            entrypoint = args["entrypoint"] if args.has_key("entrypoint") else None
            working_dir = args["working_dir"] if args.has_key("working_dir") else None
            attach_std_in = args["AttachStdin"] if args.has_key("AttachStdin") else False
            attach_std_out = args["AttachStdout"] if args.has_key("AttachStdout") else False
            attach_std_err = args["AttachStderr"] if args.has_key("AttachStderr") else False

            # headers = {'content-type': 'application/json'}
            container_config = {"Image": image, "ExposedPorts": {}}
            for key in port_bingings:
                container_config["ExposedPorts"][str(key) + "/tcp"] = {}
            if mnts_f:
                for v in mnts_f:
                    container_config["Volumes"] = {}
                    container_config["Volumes"][v] = {}
            container_config["Env"] = None
            if command is not None:
                container_config["Cmd"] = command.split(" ")
            container_config["OpenStdin"] = stdin_open
            container_config["Tty"] = tty
            container_config["Dns"] = dns
            container_config["Entrypoint"] = entrypoint
            container_config["WorkingDir"] = working_dir
            container_config["AttachStdin"] = attach_std_in
            container_config["AttachStdout"] = attach_std_out
            container_config["AttachStderr"] = attach_std_err

            #create a container
            try:
                container = self.create(vm_url, container_config, container_name)
            except:
                log.error("container %s fail to create" % container_name)
                return None


            # start_config = { "PortBindings":{"22/tcp":["10022"]}}, "Binds":[]}
            start_config = {"PortBindings": {}}

            # "Binds" = ["/host/path:/container/path:ro/rw"]
            if mnt_bindings:
                start_config["Binds"] = []
                for key in mnt_bindings:
                    start_config["Binds"].append(key + ":" + mnt_bindings[key]["bind"] + ":rw")
            for key in port_bingings:
                temp = []
                config = {"HostPort": str(port_bingings[key])}
                temp.append(config)
                start_config["PortBindings"][str(key) + "/tcp"] = temp
            result["container_id"] = container["Id"]

            # start container
            try:
                self.start(vm_url, container["Id"], start_config)
            except:
                log.error("container %s fail to start" % container["Id"])
                return None
            #print val
            #log.error("container %s fail to start" % container["Id"])
            #return None

            if self.get_container(container_name, vm_dns) is None:
                raise AssertionError("container %s fail to start" % args["name"])

        return result