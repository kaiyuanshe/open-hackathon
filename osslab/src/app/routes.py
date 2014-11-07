__author__ = "Junbo Wang"

from flask import render_template
from flask.ext.restful import reqparse, abort, Api, Resource
import json, uuid, time
from sample_course import Sample_Courses
from templates import DockerTemplates;

Template_Routes = {
    "index": "index.html",
    "PrivacyStatement": "PrivacyStatement.html",
    "TermsOfUse": "TermsOfUse.html",
    'paper': "paper.html",
    "google": "google.html",
    "head":"head.html",
    "foot":"foot.html",
    "third":"third.html",
}

running_courses = []
docker = DockerTemplates()

def get_running_course(id):
    css = filter(lambda x:x[0]==id, running_courses)
    if len(css) > 0:
        return css[0]

def delete_course(id):
    cs = get_running_course(id)
    if cs != None:
        docker.stop_containers(cs[2],cs[3])
        running_courses.remove(cs)

def simple_route(path):
    if Template_Routes.has_key(path):
        return render_template(Template_Routes[path])
    else:
        abort(404)

class CourseList(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('tag', default=None)
        args = parser.parse_args()

        kw = args['tag']
        if kw is None:
            return json.dumps(Sample_Courses)
        else:
            ret = filter(lambda c: len(filter(lambda t: kw.lower() in t.lower(), c["tags"])) > 0, Sample_Courses)
            return json.dumps(ret)


class DoCourse(Resource):
    def get(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument('c',type=int, default=1)
        args = parser.parse_args()
        # 1=vm 2=docker
        course_type = args['c']
        if name == 'flask':
            if course_type == 2:
            # todo: talk with azure to start VMs
                return "Hello python, welcome to azure"
            else:
                # call remote service to start docker containers
                course_config = json.load(file("resources/%s/%s_docker.js" % (name, name)))
                course_id = str(uuid.uuid1())
                course_context = {}
                course_context["course_id"] = course_id
                course_context["course_type"] = course_type
                try:
                    docker.start_containers(course_config, course_context)
                    running_courses.append((course_id, time.time(), course_config, course_context))
                    return json.dumps(course_context)
                except Exception as err:
                    return "fail to start due to '%s'" % err, 500
        else:
            return "the course is not ready", 404

    def delete(self, name):
        return delete_course(name)

    def put(self, name):
        cs = get_running_course(name)
        if cs != None:
            running_courses.append((name, time.time(), cs[2], cs[3]))
            running_courses.remove(cs)
        return "OK"