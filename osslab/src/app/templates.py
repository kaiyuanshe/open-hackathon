import urllib, urllib2, json
from functions import convert

def get_vm_address(context):
    # ideally its a private ip so not be restricted by port policy of azure(up to 150)
    # and the private ip should be returned by azure SDK
    # return "http://osslab1.chinacloudapp.cn:8080/"
    return "http://localhost:8000/"

class DockerTemplates(object):
    def remote_start_container(self, id, course_config, container):
        post_data = container
        post_data["uuid"] = id

        url = "http://%s/docker/%s-%s" % (container["host"], id, container["name"])
        return self.post_to_remote(url, post_data)

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

        # todo start guacamole server. Dynamic guacamole no-auth.config file is required

        servers = map(lambda c:
            self.remote_start_container(course_context["course_id"], course_config, c)
            , course_config["containers"])

        # start containers
        course_context["course_name"] = course_config["course_name"]
        course_context["servers"] = servers
        course_context["show_url"] = course_config["show_url"]
        return  True

    def stop_containers(self, course_config, course_context):
        for c in course_config["containers"]:
            url = "http://%s/docker/%s-%s" % (c["host"], course_context["course_id"], c["name"])
            self.delete_remote(url)
        return  True
