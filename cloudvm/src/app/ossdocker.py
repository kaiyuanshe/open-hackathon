__author__ = 'junbo'

from common import convert
import docker, json

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

    def get_container(self, name):
        containers = convert(self.client.containers())
        return next((c for c in containers if name in c["Names"] or '/'+name in c["Names"]), None)

    def search_containers_by_course_id(self, id):
        containers = convert(self.client.containers())
        return filter(lambda c: name_match(id, c["Names"]), containers)

    def stop(self, name):
        if self.get_container(name) is not None:
            self.client.stop(name)
            self.client.remove_container(name)
            return True
        return True

    def run(self, args):
        full_name = "%s-%s" % (args["uuid"], args["name"])
        exist = self.get_container(full_name)
        result = {
            "name": args["name"],
            "url": args["url"],
            "full_name": full_name,
            "description": args["description"]
        }
        if exist is not None:
            result["c_id"] = exist["Id"]
        else:
            image = args["image"]
            # ports foramt: [from, to ,from2, to2]. e.g.[9080,8080,3306,3306].Similar with 'mnts'
            ports = args["ports"] if args.has_key("ports") else []
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

            c_id = self.client.create_container(image,
                                         name=full_name,
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
            result["c_id"]= c_id["Id"]
            self.client.start(c_id,
                              port_bindings=port_bingings,
                              binds=mnt_bindings)

            # make sure it's running
            if self.get_container(full_name) is None:
                raise AssertionError("container %s fail to start" % args["name"])


        return result