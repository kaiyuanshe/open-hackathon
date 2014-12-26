from app.database import *
import urllib2, json
from app.log import *

def post():
    """
    expr = Experiment.query.filter_by(status=2).first()
    for c in expr.containers.filter(DockerContainer.image != 'hall/guacamole').all():
        for p in c.port_bindings:
            print p
    vm=HostServer.query.all()
    print vm
    """
    name = "web"
    url = "http://localhost:4243/containers/create?name=%s"
    url1 = "http://localhost:4243/images/json"
    postdata = {
        "Hostname": "",
        "Domainname": "",
        "User": "",
        "Memory": 0,
        "MemorySwap": 0,
        "CpuShares": 512,
        "Cpuset": "0,1",
        "AttachStdin": False,
        "AttachStdout": True,
        "AttachStderr": True,
        "Tty": False,
        "OpenStdin": False,
        "StdinOnce": False,
        "Env": None,
        "Cmd": [
            "date"
        ],
        "Entrypoint": "",
        "Image": "ubuntu",
        "Volumes": {
            "/tmp": {}
        },
        "WorkingDir": "",
        "NetworkDisabled": False,
        "MacAddress": "12:34:56:78:9a:bc",
        "ExposedPorts": {
            "22/tcp": {}
        },
        "SecurityOpts": [""],
        "HostConfig": {
            "Binds": ["/tmp:/tmp"],
            "Links": ["redis3:redis"],
            "LxcConf": {"lxc.utsname": "docker"},
            "PortBindings": {"22/tcp": [{"HostPort": "11022"}]},
            "PublishAllPorts": False,
            "Privileged": False,
            "Dns": ["8.8.8.8"],
            "DnsSearch": [""],
            "VolumesFrom": ["parent", "other:ro"],
            "CapAdd": ["NET_ADMIN"],
            "CapDrop": ["MKNOD"],
            "RestartPolicy": {"Name": "", "MaximumRetryCount": 0},
            "NetworkMode": "bridge",
            "Devices": []
        }
    }
    jdata = json.dumps(postdata)
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')

    f = urllib2.urlopen(req, jdata)
    print f.read()

def stop():
    try:
        name = "16-web"
        #url = "http://localhost:4243/containers/create"
        #headers = {"User-Agent":"Mozilla/4.0(compatible; MSIE 6.0; Windows NT 5.1)"}
        url = "http://localhost:4243/containers/%s/stop"%name
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        response = urllib2.urlopen(url, "")
    except Exception as e:
        log.error(e)

def get():
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    url = 'http://localhost:4243/containers/json'
    request = urllib2.Request(url)
    resp = opener.open(request)
    print resp.read()

if __name__ == '__main__':
    stop()