from flask import Flask, request
from flask.ext.restful import reqparse, abort, Api, Resource
from time import gmtime, strftime
from gittle import Gittle
from app import app
from scm import SCM
from common import *
from ossdocker import OssDocker
from log import log
import json, shutil, os
import xml.dom.minidom as minidom
from os.path import realpath, dirname

api = Api(app)
docker = OssDocker()
start_time = strftime("%Y-%m-%d %H-%M-%S", gmtime())

# make sure OSSLAB_RUN_DIR is writable by the running user: the current user if run in cmd or www-data in apache2.
# don't use sudo because you cannot always run your code in sudo e.g. apache2 service
OSSLAB_RUN_DIR = "/var/lib/osslab"


def json_type(data):
    try:
        return json.load(data)
    except:
        raise ValueError('Malformed JSON')


def course_path(id, sub=None):
    if sub is None:
        return "%s/%s" % (OSSLAB_RUN_DIR, id)
    else:
        return "%s/%s/%s" % (OSSLAB_RUN_DIR, id, sub)


class Health(Resource):
    def get(self):
        try:
            health = {
                "status": "OK",
                "start_time": start_time,
                "report_time": strftime("%Y-%m-%d %H-%M-%S", gmtime()),
                "docker": docker.health()
            }
            return health
        except Exception as err:
            log.error(err)
            return {
                "status": "Error",
                "start_time": start_time,
                "report_time": strftime("%Y-%m-%d %H-%M-%S", gmtime()),
            }


class DockerManager(Resource):
    def post(self):
        try:
            # ====================================================test data start
            # example1:
            # {"expr_id":"abcde", "name":"flask", "image": "verdverm/flask","ports":[15000,5000],"mnt":["/tmp/docker/abcde/flask/src","/src"],"detach":true}
            # example2(guacamole):
            # {"expr_id":"uuid", "name":"flask", "image": "hall/guacamole","ports":[18080,8080],"detach":true,
            # "guacamole_config":[{"name":"web","protocol":"ssh","hostname":"42.159.236.228","port":"63025","username":"opentech","password":"@dministrat0r"}]}
            #
            # ====================================================test data end

            args = convert(request.get_json())
            expr_id = args["expr_id"]
            mnts = args["mnt"] if args.has_key("mnt") else []
            # todo parameters validation

            guaca = args["guacamole_config"] if args.has_key("guacamole_config") else None
            if guaca is not None:
                guaca_dir = course_path(expr_id, "guacamole")
                mkdir_safe(guaca_dir)
                src_prop_file = "%s/resources/guacamole.properties" % dirname(realpath(__file__))
                shutil.copyfile(src_prop_file, "%s/%s" % (guaca_dir, "guacamole.properties"))

                # generate guacamole config
                impl = minidom.getDOMImplementation()
                dom = impl.createDocument(None, "configs", None)
                root = dom.documentElement

                def app(rt, cfg):
                    cn = dom.createElement("config")
                    for (d, x) in cfg.items():
                        if d == "name" or d == "protocol":
                            cn.setAttribute(d, x)
                        else:
                            param = dom.createElement("param")
                            param.setAttribute("name", d)
                            param.setAttribute("value", str(x))
                            cn.appendChild(param)
                    rt.appendChild(cn)

                map(lambda cfg: app(root, cfg), guaca)
                f = open("%s/%s" % (guaca_dir, "noauth-config.xml"), "w")
                dom.writexml(f, addindent="  ", newl="\n", encoding="utf-8")
                f.close()

                mnts.append(guaca_dir)
                mnts.append("/etc/guacamole")
                args["mnt"] = mnts
                docker.run(args)

        except Exception as err:
            log.error(err)
            return "fail to start due to '%s'" % err, 500

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cname', type=str)
        args = parser.parse_args()
        name = args["cname"]

        docker.stop(name)

        return "OK"


class SourceCode(Resource):
    def post(self):
        try:
            # ====================================================test data start
            # {"expr_id":"abcde", "repo_name":"flask","repo_url":"https://github.com/juniwang/flask-example.git"}
            # ====================================================test data end
            scm = convert(request.get_json())
            local_repo_path = course_path(scm["expr_id"], scm["repo_name"])
            scm["local_repo_path"] = local_repo_path

            if os.path.exists(local_repo_path):
                shutil.rmtree(local_repo_path)

            # checkout code from git
            provider = SCM(scm["provider"] if scm.has_key("provider") else "git")
            provider.clone(scm)
            return scm
        except Exception as err:
            log.error(err)
            return "fail to clone source code", 500

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('expr_id')
        parser.add_argument('repo_name')
        args = parser.parse_args()

        local_repo_path = course_path(args["expr_id"], args["repo_name"])
        shutil.rmtree(local_repo_path)

        return "OK"


api.add_resource(Health, '/')
api.add_resource(DockerManager, '/docker')
api.add_resource(SourceCode, '/scm')