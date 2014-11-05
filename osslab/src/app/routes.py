__author__ = "Junbo Wang"

from flask import render_template
from flask.ext.restful import reqparse, abort, Api, Resource
import json

Template_Routes = {
    "index": "index.html",
    "PrivacyStatement": "PrivacyStatement.html",
    "TermsOfUse": "TermsOfUse.html",
    'paper': "paper.html",
    "google": "google.html"
}

Courses = [
    {
        "id": "flask",
        "name": "Python+Flask",
        "create_time": "2014-10-25",
        "like_count": 330,
        "description": "Python on Flask",
        "tags": ["python", "flask", "web", "web framework", "python web framework"]
    },
    {
        "id": "django",
        "name": "Python+Django",
        "create_time": "2014-10-25",
        "like_count": 10,
        "description": "Python on Django",
        "tags": ["python", "django", "web", "web framework", "python web framework", "MVC", "mvc framework"]
    },
    {
        "id": "pyramid",
        "name": "Python+Pyramid",
        "create_time": "2014-10-25",
        "like_count": 320,
        "description": "Python on Pyramid",
        "tags": ["python", "pyramid", "web", "web framework", "python web framework"]
    },
    {
        "id": "tornado",
        "name": "Python+Tornado",
        "create_time": "2014-10-25",
        "like_count": 130,
        "description": "Python on Tornado",
        "tags": ["python", "tornado", "web", "web framework", "python web framework"]
    },
    {
        "id": "beego",
        "name": "Go+Beego",
        "create_time": "2014-10-25",
        "like_count": 303,
        "description": "GO on Beego",
        "tags": ["go", "golang", "beego", "web framework", "golang web framework", "web"]
    },
    {
        "id": "rails",
        "name": "Ruby+Rails",
        "create_time": "2014-10-25",
        "like_count": 23,
        "description": "Ruby on Rails",
        "tags": ["ruby", "rails", "web", "web framework", "ruby web framework", "MVC", "mvn framework"]
    },
    {
        "id": "sinatra",
        "name": "Ruby+Sinatra",
        "create_time": "2014-10-25",
        "like_count": 30,
        "description": "Ruby on Sinatra",
        "tags": ["ruby", "sinatra", "web", "web framework", "ruby web framework"]
    },
    {
        "id": "MEAN",
        "name": "Python+Flask",
        "create_time": "2014-10-25",
        "like_count": 30,
        "description": "Python on Flask",
        "tags": ["python", "flask", "web", "web framework", "python web framework"]
    },
    {
        "id": "flask",
        "name": "Python+Flask",
        "create_time": "2014-10-25",
        "like_count": 30,
        "description": "Python on Flask",
        "tags": ["python", "flask", "web", "web framework", "python web framework"]
    },
    {
        "id": "flask",
        "name": "Python+Flask",
        "create_time": "2014-10-25",
        "like_count": 30,
        "description": "Python on Flask",
        "tags": ["python", "flask", "web", "web framework", "python web framework"]
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