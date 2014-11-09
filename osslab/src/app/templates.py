import urllib, urllib2, json
from functions import convert
from compiler.ast import flatten

def get_vm_address(context):
    # todo get availabe VM
    # 1. ideally its a private ip so not be restricted by port policy of azure(up to 150)
    # and the private ip should be returned by azure SDK
    # 2. the data should come from DB where we know how many VMs are there, how many containers are
    # capable, and which ports are available
    # 3. if no VM is ready, we should call azure api to create a new one. The new-created VM must run 'cloudvm'
    # service by default(either cloud-init or python remote ssh)
    # 4. keep the private in DB for guacamole server too
    return "localhost:8001"

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
            ps= map(lambda p: [10000+p, p], container["ports"])
            container["ports"]= flatten(ps)
        if container.has_key("mnt"):
            mnts_with_repo = map(lambda s: s if "%s" not in s else s % course_context["local_repo_path"], container["mnt"])
            container["mnt"]= mnts_with_repo

        # add to guacamole config
        # note the port should get from the container["port"] to get corresponding listening port rather than the
        # expose port that defined in the template. Following codes are just example
        if container.has_key("guacamole"):
            guac= container["guacamole"]
            gc= {
                "name": container["name"],
                "protocol": guac["protocol"],
                "host": "localhost",
                "port": 10000+guac["port"]
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

    def delete_remote(self, url):
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url)
        request.get_method = lambda : 'DELETE'
        resp = opener.open(request)
        return "OK"

    def start_containers(self, course_config, course_context):

        # get available VM that runs the cloudvm and is available for more containers
        vm_host= get_vm_address(course_context)
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
                "ports": [8080],
                "detach": True,
                "guacamole_config": guacamole_config
            }
            self.remote_start_container(course_context, guacamole_container, [])

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
