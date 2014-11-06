__author__ = "Junbo Wang"

from flask import render_template
from flask.ext.restful import reqparse, abort, Api, Resource
import json

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

Courses = [
    {
        "name": "flask",
        "create_time": "2014-10-25",
        "like_count": 30,
        "description": "Python on Flask",
        "tags": ["python", "mvc", "flask", "web"]
    },
    {
        "name": "ruby on rails",
        "create_time": "2014-10-25",
        "like_count": 32,
        "description": "Ruby on Rails",
        "tags": ["ruby", "mvc", "rails", "web"]
    }
]

def simple_route(path):
    if Template_Routes.has_key(path):
        return render_template(Template_Routes[path])
    else:
        abort(404)

class CourseList(Resource):
    def get(self):
        return json.dumps(Courses)