from app.database import *
import urllib2, json
from app.log import *
id = ""
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
    name1 = "web6"
    url = "http://localhost:4243/containers/create?name=%s" % name1
    #url1 = "http://localhost:4243/images/json"
    testdata = {'Tty': True,
                'Volumes': [],
                'Image': 'rastasheep/ubuntu-sshd:latest',
                'Cmd': "",
                'WorkingDir': None,
                'Dns': None,
                'Entrypoint': None,
                'Env': None,
                'AttachStdin':False,
                'AttachStdout': True,
                'AttachStderr': True,
                'ExposedPorts':{
                    "80/tcp":{}
                },
                'PortBindings':{80: 10080, 22:10056},
                'OpenStdin': True
    }

    testdata1 = {'Tty': True,
                 'Volumes': [],
                 'Image': 'rastasheep/ubuntu-sshd:latest',
                 'Cmd': "",
                 'WorkingDir': None,
                 'Dns': None,
                 'Entrypoint': None,
                 'Env': None,
                 'AttachStdin': False,
                 'AttachStderr': True,
                 'AttachStdout': True,

                 'OpenStdin': True
    }
    jdata = json.dumps(testdata1)
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    f = urllib2.urlopen(req, jdata)

    c_id = json.loads(f.read())
    id = c_id["Id"]
    url = "http://localhost:4243/containers/%s/start"%id
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    start_ = {
            "Binds" : [],
            'PortBindings':
                {
                    "80/tcp":[{"HostPort":"10080"}]
                }
    }
    response = urllib2.urlopen(url, "")
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
def start():
    try:
        #id = "942491ccb0d2"
        #url = "http://localhost:4243/containers/create"
        #headers = {"User-Agent":"Mozilla/4.0(compatible; MSIE 6.0; Windows NT 5.1)"}
        url = "http://localhost:4243/containers/%s/start"%id
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        portdata = {
            "Binds" : ["/tmp:/tmp"],
            'PortBindings':{"22/tcp":[{"HostPort":"11022"}]}
        }
        response = urllib2.urlopen(url, " ")
    except Exception as e:
        log.error(e)

def get():
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    url = 'http://localhost:4243/containers/json'
    request = urllib2.Request(url)
    resp = opener.open(request)
    print resp.read()

if __name__ == '__main__':
    post()
