__author__ = "Junbo Wang"

from flask import render_template
from flask.ext.restful import reqparse, abort, Api, Resource
import json
from osscourses import Sample_Courses

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
