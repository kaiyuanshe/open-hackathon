from flask import Flask, request
from flask.ext.restful import reqparse, abort, Api, Resource
from time import gmtime, strftime
from gittle import Gittle
from app import app
from scm import SCM
from common import convert
from ossdocker import OssDocker
import json, shutil

api = Api(app)
docker = OssDocker()
start_time = strftime("%Y-%m-%d %H-%M-%S", gmtime())

def json_type(data):
    try:
        return json.load(data)
    except:
        raise ValueError('Malformed JSON')



class Health(Resource):
    def get(self):
        health = {
            "status": "OK",
            "start_time": start_time,
            "report_time": strftime("%Y-%m-%d %H-%M-%S", gmtime())
        }
        return json.dumps(health)

class DockerManager(Resource):
    def get(self, name):
        return name

    def post(self, name):
        try:
            args = convert(request.get_json())

            # todo parameters validation

            # checkout source code if needed
            scm = args["scm"] if args.has_key("scm") else None
            if scm is not None:
                repo_path = '/tmp/docker/%s/%s' % (args["uuid"], args["name"])
                scm["local_repo_path"] = repo_path

                # checkout code from git
                provider = SCM(args["scm"]["provider"])
                provider.clone(scm)

            return json.dumps(docker.run(args))
        except Exception as err:
            return "fail to start due to '%s'" % err, 500

    def delete(self, name):
        docker.stop(name)
        id = name[:name.rfind('-')]
        app = name[name.rfind('-'):]
        shutil.rmtree('/tmp/docker/%s/%s' % (id, app), ignore_errors=True)
        # remove src code folder for whole course
        if len(docker.search_containers_by_course_id(id)) == 0:
            shutil.rmtree("/tmp/docker/%s" % id, ignore_errors=True)

        return  "OK"


api.add_resource(Health, '/')
api.add_resource(DockerManager, '/docker/<string:name>')