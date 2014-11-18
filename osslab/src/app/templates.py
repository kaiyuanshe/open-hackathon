import urllib, urllib2, json
from functions import convert
from compiler.ast import flatten

def get_vm_private_host(context):
    # todo get availabe VM
    # 1. ideally its a private ip so not be restricted by port policy of azure(up to 150)
    # and the private ip should be returned by azure SDK
    # 2. the data should come from DB where we know how many VMs are there, how many containers are
    # capable, and which ports are available
    # 3. if no VM is ready, we should call azure api to create a new one. The new-created VM must run 'cloudvm'
    # service by default(either cloud-init or python remote ssh)
    # 4. keep the private IP in DB for guacamole server too

    # return "10.0.2.15"
    return "10.207.250.79"

def get_cloudvm_address(context):
    # the port is that cloudvm service is listening on. 8001 by default
    # connect to cloudvm service through its private address when deploy on azure. Here its public address used for
    # debug purpose
    return "%s:%s" % (get_vm_public_host(context), 8001)

def get_vm_public_host(context):
    # sure it must get from DB and it must accessible from public so it's a CloudService endpoint in general.

    # return "localhost"
    return "osslab1.chinacloudapp.cn"

def get_available_port(port_cfg, course_context):
    # get an available on the target VM. host_port means the port that listening on the host VM.
    # you should see port forward ruls "host_port -> port" on docker status(docker ps) after contain created.
    # again, the data should be in DB
    if not "host_port" in port_cfg:
        port_cfg["host_port"] = port_cfg["port"] + 10000

    # output: not well designed ,need re-design
    if port_cfg.has_key("public"):

        # todo open port on azure for those must open to public
        # public port means the port open the public. For azure , it's the public port on azure. There
        # should be endpoint on azure that from public_port to host_port
        # need design first
        if not "public_port" in port_cfg:
            port_cfg["public_port"] = port_cfg["host_port"]

        op = course_context["output"] if course_context.has_key("output") else []
        op.append("http://%s:%s" % (get_vm_public_host(course_context), port_cfg["public_port"]))
        course_context["output"]= op


    return port_cfg["host_port"]

class DockerTemplates(object):
    def remote_start_container(self, course_context, container, guacamole_config):
        post_data = container
        post_data["course_id"] = course_context["course_id"]

        # format data in the template such as port and mnt.
        # the port defined in template have only expose port, we should assign a listening port in program
        # the mnt may contain placeholder for source code dir which are decided by 'cloudvm' service
        if container.has_key("ports"):
            # get an available on the target VM
            # again, the data should be in DB
            ps= map(lambda p: [get_available_port(p, course_context), p["port"]], container["ports"])
            container["docker_ports"]= flatten(ps)
        if container.has_key("mnt"):
            mnts_with_repo = map(lambda s: s if "%s" not in s else s % course_context["local_repo_path"], container["mnt"])
            container["mnt"]= mnts_with_repo

        # add to guacamole config
        # note the port should get from the container["port"] to get corresponding listening port rather than the
        # expose port that defined in the template. Following codes are just example
        if container.has_key("guacamole") and container.has_key("ports"):
            guac= container["guacamole"]
            port_cfg= filter(lambda p: p["port"]==guac["port"], container["ports"])

            if len(port_cfg) > 0:
                gc= {
                    "name": port_cfg[0]["name"] if port_cfg[0].has_key("name") else container["name"],
                    "protocol": guac["protocol"],
                    "hostname": get_vm_private_host(course_context), # get from DB rather than from config template
                    "port": port_cfg[0]["host_port"]
                }
                if guac.has_key("username"):
                    gc["username"]= guac["username"]
                if guac.has_key("password"):
                    gc["password"]= guac["password"]

                guacamole_config.append(gc)

        # start container remotely
        url = "http://%s/docker" % course_context["vm_host"]
        return self.post_to_remote(url, post_data)

    def remote_checkout(self, host, course_id, scm):
        post_data = scm
        post_data["course_id"] = course_id

        url= "http://%s/scm" % host
        return  self.post_to_remote(url, post_data)

    # move to common.py for re-use
    def post_to_remote(self, url, post_data):
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        f = urllib2.urlopen(req, json.dumps(post_data))
        resp = f.read()
        f.close()
        return convert(json.loads(resp))

    def get_remote(self, url):
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url)
        resp = opener.open(request)
        return resp.read()

    def delete_remote(self, url):
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url)
        request.get_method = lambda : 'DELETE'
        resp = opener.open(request)
        return "OK"

    def query_guaca_status(self, course_context):
        try:
            self.get_remote("http://%s:%s" % (get_vm_public_host(course_context), 9080))
            course_context["guacamole_status"] = True
        except:
            course_context.pop("guacamole_status", None)

    def start_containers(self, course_config, course_context):

        # get available VM that runs the cloudvm and is available for more containers
        vm_host= get_cloudvm_address(course_context)
        course_id= course_context["course_id"]
        course_context["vm_host"]= vm_host
        guacamole_config= []

        # checkout source code
        if course_config.has_key("scm"):
            scm_ret= self.remote_checkout(vm_host, course_id, course_config["scm"])
            course_context["local_repo_path"]= scm_ret["local_repo_path"]

        # start containers
        servers = map(lambda container:
            self.remote_start_container(course_context, container, guacamole_config)
            , course_config["containers"])

        # start guacamole
        if len(guacamole_config) > 0:
            # also, the guacamole port should come from DB
            guacamole_container= {
                "name": "guacamole",
                "course_id": course_id,
                "image": "hall/guacamole",
                "ports": [{
                    "name": "guacamole",
                    "port": 8080,
                    "host_port": 9080,
                    "public_port": 9080,
                    "public": True
                }],
                "detach": True,
                "guacamole_config": guacamole_config
            }

            self.remote_start_container(course_context, guacamole_container, [])

            # return guacamole link to frontend
            def to_op(config):
                url= "http://%s:%s/client.xhtml?id=" % (get_vm_public_host(course_context), guacamole_container["ports"][0]["public_port"]) + "c%2F" + config["name"]
                return {
                    "name": config["name"],
                    "url": url
                }
            course_context["guacamole_servers"]= map(lambda cfg: to_op(cfg), guacamole_config)

        # response to client
        course_context["course_name"] = course_config["course_name"]
        course_context["servers"] = servers
        return  True

    def stop_containers(self, course_config, course_context):
        guaca= False
        for c in course_config["containers"]:
            if c.has_key("guacamole"):
                guaca= True
            url = "http://%s/docker?cname=%s-%s" % (course_context["vm_host"], course_context["course_id"], c["name"])
            self.delete_remote(url)

        # remove guacamole container
        if guaca:
            url = "http://%s/docker?cname=%s-%s" % (course_context["vm_host"], course_context["course_id"], "guacamole")
            self.delete_remote(url)
        return  True
