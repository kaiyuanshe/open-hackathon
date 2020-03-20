# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

"""the input and output schemas of hackathon RESTFul APIs

The basic hierarchy is schemas[NameOfResourceClass][HTTP Method]["input"/"output"][schema of api].
For example, schemas["HealthResource"]["get"]["output"] defines the output format for "HealthResource GET" api.
Hackathon responses defined in hackathon_response.py for error won't be checked.

Refer to http://validictory.readthedocs.org/en/latest/usage.html about how to define schema

For hackathon server APIs:
    - Resource that needs to enable input/output validation should inherit from 'HackathonResource' rather than
'flask_restful.Resource'. In other word, if validation if unnecessary for your API, for example file upload API,
inherit from 'flask_restful.Resource' to disable the validation.
    - If not all http methods are to validate(You want to POST to be validated but GET not), or either input or output
validation is unnecessary, it's very simply by just deleting the specific key from schemas.
    - As a convention, 'description' MUST be included in every schema. And say enough in all descriptions
to make sure it's understandable by anyone. 'description' MUST be included in every property too.
    - You can define all schemas here or add a json file in 'schema' folder.It's better we create a dedicate json file
for each Resource to prevent this file from being too large.
    - For the output, you can only define schemas for those required properties
"""
from os import listdir
from os.path import isfile, join, dirname, realpath
import json
from hackathon.log import log

__all__ = [
    "schemas"
]

schemas = {}

# schema for api "/" and "/health"
schemas["CurrentTimeResource"] = {
    "get": {
        "output": {
            "title": "response to get current time of hackathon server",
            "description": "get current time of hackathon server so that client can show right count down time",
            "type": "object",
            "properties": {
                "currenttime": {
                    "type": "number",
                    "description": "time in miliseconds"
                }
            }
        }
    }
}

schema_dir = join(dirname(realpath(__file__)), "schema")
json_files = [join(schema_dir, f) for f in listdir(schema_dir) if isfile(join(schema_dir, f))]

for js_file in json_files:
    try:
        with open(js_file) as fs:
            schemas.update(json.load(fs))
    except Exception as e:
        log.debug("[server api_schema] %s" % str(e)) 