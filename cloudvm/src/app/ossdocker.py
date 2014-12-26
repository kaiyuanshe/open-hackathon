__author__ = 'junbo'

from common import convert
import docker, json
#new
import urllib2
import log
#end

def name_match(id, l):
    for n in l:
        if id in n:
            return True

    return False

class OssDocker(object):
    def __init__(self):
        self.client = docker.Client(base_url='unix://var/run/docker.sock',
                                    version='1.12',
                                    timeout=20)
        #new
        self.base_url = "http://localhost:4243"
        #end

    #new
    def containers(self):
        try:
            containers_url = self.base_url + "/containers/json"
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            request = urllib2.Request(containers_url)
            resp = opener.open(request)
            return convert(json.loads(resp.read()))
        except Exception as e:
            log.error(e)
    #end

    def get_container(self, name):
        #new
        containers_test = self.containers()
        return next((c for c in containers_test if name in c["Names"] or '/'+name in c["Names"]), None)
        #end

        #origin
        #containers = convert(self.client.containers())
        #return next((c for c in containers if name in c["Names"] or '/'+name in c["Names"]), None)

    def search_containers_by_expr_id(self, id, all=False):
        #new
        containers_test = self.containers()
        return filter(lambda c: name_match(id, c["Names"]), containers_test)
        #end

        #origin
        #containers = convert(self.client.containers(all=all))
        #return filter(lambda c: name_match(id, c["Names"]), containers)

    def stop(self, name):
        if self.get_container(name) is not None:
            #new
            try:
                url = "http://localhost:4243/containers/%s/stop" % name
                urllib2.urlopen(url, "")
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
        containers_test = self.containers()
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
            mnts_f = map(lambda s: s if "%s" not in s or not args.has_key("scm") else s % args["scm"]["local_repo_path"], mnts[::2])
            mnts_t = map(lambda s: {"bind":s,"ro":False}, mnts[1::2])
            mnt_bindings = dict(zip(mnts_f, mnts_t))

            env = args["environments"] if args.has_key("environments") else {}
            detach = args["detach"] if args.has_key('detach') else False
            command = args["command"] if args.has_key('command') else None
            stdin_open =args["stdin_open"] if args.has_key("stdin_open") else False
            tty =args["tty"] if args.has_key("tty") else False
            dns =args["dns"] if args.has_key("dns") else None
            entrypoint =args["entrypoint"] if args.has_key("entrypoint") else None
            working_dir =args["working_dir"] if args.has_key("working_dir") else None

            #new
            container_config = {}
            container_config["Image"] = image
            container_config["Ports"] = ports[1::2]
            container_config["Volumes"] = mnts[1::2]
            container_config["Env"] = env
            container_config["Cmd"] = command
            container_config["OpenStdin"] = stdin_open
            container_config["Tty"] = tty
            container_config["Dns"] = dns
            container_config["Entrypoint"] = entrypoint
            container_config["WorkingDir"] = working_dir
            containers_url = self.base_url + "/containers/create?name=%s" % container_name
            req = urllib2.Request(containers_url)
            req.add_header('Content-Type', 'application/json')
            test = urllib2.urlopen(containers_url, json.dumps(container_config))
            c_id = json.loads(test)
            #end

            #origin
            """c_id = self.client.create_container(image,
                                         name=container_name,
                                         ports=ports[1::2],
                                         volumes=mnts[1::2],
                                         environment=env,
                                         detach=detach,
                                         command=command,
                                         stdin_open=stdin_open,
                                         tty=tty,
                                         dns=dns,
                                         entrypoint=entrypoint,
                                         working_dir=working_dir)
            """
            result["container_id"]= c_id["Id"]
            self.client.start(c_id,
                              port_bindings=port_bingings,
                              binds=mnt_bindings)

            # make sure it's running
            if self.get_container(container_name) is None:
                raise AssertionError("container %s fail to start" % args["name"])


        return result