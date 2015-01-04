__author__ = 'junbo'

from common import convert
import docker, json, requests
# new
import log
#end

def name_match(id, l):
    for n in l:
        if id in n:
            return True

    return False


class OssDocker(object):
    def __init__(self):
        #self.client = docker.Client(base_url='unix://var/run/docker.sock',
        #                            version='1.12',
        #                            timeout=20)
        #new
        self.base_url = "http://localhost:4243"
        self.headers = {'content-type': 'application/json'}
        #end

    #new
    def containers_info(self):
        try:
            containers_url = self.base_url + "/containers/json"
            req = requests.get(containers_url)
            return convert(json.loads(req.content))
        except Exception as e:
            log.error(e)

    #end

    def get_container(self, name):
        #new
        containers_test = self.containers_info()
        return next((c for c in containers_test if name in c["Names"] or '/' + name in c["Names"]), None)
        #end

        #origin
        #containers = convert(self.client.containers())
        #return next((c for c in containers if name in c["Names"] or '/'+name in c["Names"]), None)

    def search_containers_by_expr_id(self, id, all=False):
        #new
        get_containers = self.containers_info()
        return filter(lambda c: name_match(id, c["Names"]), get_containers)
        #end

        #origin
        #containers = convert(self.client.containers(all=all))
        #return filter(lambda c: name_match(id, c["Names"]), containers)

    def stop(self, name):
        if self.get_container(name) is not None:
            #new
            try:
                containers_url = "http://localhost:4243/containers/%s/stop" % name
                requests.post(containers_url)
            except Exception as e:
                log.error(e)
            #end
            #origin
            #self.client.stop(name)
            # self.client.remove_container(name)
            return True
        return True

    def health(self):
        #new
        containers_test = self.containers_info()
        return {
            "status": "OK",
            "container_count": len(containers_test)
        }
        #end

        #origin
        #containers = convert(self.client.containers())
        #return {
        #    "status": "OK",
        #    "container_count": len(containers)
        #}

    def run(self, args):
        container_name = args["container_name"]
        exist = self.get_container(container_name)
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

            env = args["environments"] if args.has_key("environments") else {}
            detach = args["detach"] if args.has_key('detach') else False
            command = args["command"] if args.has_key('command') else None
            stdin_open = args["stdin_open"] if args.has_key("stdin_open") else False
            tty = args["tty"] if args.has_key("tty") else False
            dns = args["dns"] if args.has_key("dns") else None
            entrypoint = args["entrypoint"] if args.has_key("entrypoint") else None
            working_dir = args["working_dir"] if args.has_key("working_dir") else None

            #new
            #headers = {'content-type': 'application/json'}
            container_config = {}
            container_config["Image"] = image
            container_config["ExposedPorts"] = {}
            for key in port_bingings:
                container_config["ExposedPorts"][str(key) + "/tcp"] = {}
            if mnts_f is not None:
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
            container_config['AttachStdin'] = False,
            container_config['AttachStdout'] = True,
            container_config['AttachStderr'] = True,
            containers_url = self.base_url + "/containers/create?name=%s" % container_name
            req_create = requests.post(containers_url, data=json.dumps(container_config), headers=self.headers)

            c_id = json.loads(req_create.content)

            #start container
            #start_config = { "PortBindings":{"22/tcp":["10022"]}}, "Binds":[]}
            start_config = {}
            start_config["PortBindings"] = {}

            #"Binds" = ["/host/path:/container/path:ro/rw"]
            if mnt_bindings:
                start_config["Binds"] = []
                for key in mnt_bindings:
                    start_config["Binds"].append(key + ":" + mnt_bindings[key]["bind"] + ":rw")
            for key in port_bingings:
                temp = []
                config = {}
                config["HostPort"] = str(port_bingings[key])
                temp.append(config)
                start_config["PortBindings"][str(key) + "/tcp"] = temp
            #print start_config
            result["container_id"] = c_id["Id"]
            #new
            try:
                url = "http://localhost:4243/containers/%s/start" % c_id["Id"]
                requests.post(url, data=json.dumps(start_config), headers=self.headers)
                #print req_start.content
            except Exception as e:
                log.error(e)
            #end

            #origin
            #c_id = self.client.create_container(image,
            #                             name=container_name,
            #                             ports=ports[1::2],
            #                             volumes=mnts[1::2],
            #                             environment=env,
            #                             detach=detach,
            #                             command=command,
            #                             stdin_open=stdin_open,
            #                             tty=tty,
            #                             dns=dns,
            #                             entrypoint=entrypoint,
            #                             working_dir=working_dir)
            #"""

            #end
            #origin
            #self.client.start(c_id,
            #                  port_bindings=port_bingings,
            #                  binds=mnt_bindings)
            # make sure it's running
            if self.get_container(container_name) is None:
                raise AssertionError("container %s fail to start" % args["name"])

        return result