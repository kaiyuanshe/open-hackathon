from os.path import realpath, dirname
from flask_restful import Resource, reqparse
from . import api
from expr import expr_manager
from database.models import *
from user.login import *
from flask import g, request
from log import log
from database import db_adapter
from decorators import token_required
from sqlalchemy import and_, or_


class RegisterListResource(Resource):
    # =======================================================return data start
    # [{"register_name":"zhang", "online":"1","submitted":"0"..."description":" "}]
    # =======================================================return data end
    @token_required
    def get(self):
        json_ret = map(lambda u: u.json(), user_manager.get_all_registration())
        return json_ret


class UserExperimentResource(Resource):
    # user experiment id
    @token_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args')
        args = parser.parse_args()
        if args['id'] is None:
            return json.dumps({"error": "Bad request"}), 400
        cs = expr_manager.get_expr_status(args['id'])
        if cs is not None:
            return cs
        else:
            return "Not Found", 404

    @token_required
    def post(self):
        args = request.get_json()
        if "cid" not in args or "hackathon" not in args:
            return "invalid parameter", 400
        cid = args["cid"]
        hackathon = args["hackathon"]
        template_file = "%s/resources/%s-%s.js" % (dirname(realpath(__file__)), hackathon, cid)
        if os.path.isfile(template_file):
            # call remote service to start docker containers
            expr_config = json.load(file(template_file))
            try:
                return expr_manager.start_expr(hackathon, expr_config)
            except Exception as err:
                log.error(err)
                return "fail to start due to '%s'" % err, 500
        else:
            return "the experiment %s is not ready" % id, 404

    @token_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args')
        args = parser.parse_args()
        if args['id'] is None:
            return json.dumps({"error": "Bad request"}), 400

        return expr_manager.stop_expr(args["id"])

    @token_required
    def put(self):
        args = request.get_json()
        if args['id'] is None:
            return json.dumps({"error": "Bad request"}), 400
        return expr_manager.heart_beat(args["id"])


class BulletinResource(Resource):
    def get(self):
        return db_adapter.find_first_object(Announcement, enabled=1).json()

    # todo bulletin post
    @token_required
    def post(self):
        pass


class LoginResource(Resource):
    def post(self):
        body = request.get_json()
        provider = body["provider"]
        return login_providers[provider].login(body)

    @token_required
    def delete(self):
        return login_providers.values()[0].logout(g.user)


# todo health page
class HealthResource(Resource):
    def get(self):
        return {
            "status": "OK"
        }


class HackathonResource(Resource):
    # id is hackathon id
    @token_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args')
        args = parser.parse_args()
        if args['id'] is None:
            return {"error": "Bad request"}, 400
        return db_adapter.find_first_object(Hackathon, id=args['id']).json()

    # todo hackathon post
    @token_required
    def post(self):
        pass


class HackathonListResource(Resource):
    def get(self):
        return map(lambda u: u.json(), db_adapter.find_all_objects(Hackathon))


class HackathonStatResource(Resource):
    # id is hackathon id
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args')
        args = parse.parse_args()
        if args['id'] is None:
            return json.dumps({"error": "Bad request"}), 400
        total_num = Register.query.filter(Register.hackathon_id == args['id']).count()
        enabled_num = Register.query.filter(Register.hackathon_id == args['id'], Register.enabled == 1).count()
        disabled_num = Register.query.filter(Register.hackathon_id == args['id'], Register.enabled == 0).count()
        return {'id': args['id'], 'total': total_num, 'online': enabled_num, 'offline': disabled_num}


class UserHackathonResource(Resource):
    # id is user id
    @token_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args')
        args = parse.parse_args()
        if args['id'] is None:
            return json.dumps({"error": "Bad request"}), 400
        hackathon = map(lambda u: u.hackathon.json(),
                   Experiment.query.filter(and_(Experiment.user_id == args['id'], Experiment.status < 5)).all())
        unique_hackathon = [x for x in set(hackathon)]
        return unique_hackathon

    # todo user hackathon post
    @token_required
    def post(self):
        pass

    # todo delete user hackathon
    @token_required
    def delete(self):
        pass


class HackathonTemplateResource(Resource):
    def get(self):
        return map(lambda u: u.json(), db_adapter.find_all_objects(Template))


class UserExperimentListResource(Resource):
    # id is user id
    @token_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args')
        args = parse.parse_args()
        if args['id'] is None:
            return json.dumps({"error": "Bad request"}), 400
        return map(lambda u: u.json(),
                   Experiment.query.filter(and_(Experiment.user_id == args['id'], Experiment.status < 5)).all())


api.add_resource(BulletinResource, "/api/bulletin")
api.add_resource(LoginResource, "/api/user/login")
api.add_resource(HackathonResource, "/api/hackathon")
api.add_resource(HackathonListResource, "/api/hackathon/list")
api.add_resource(HackathonTemplateResource, "/api/hackathon/template")
api.add_resource(HackathonStatResource, "/api/hackathon/stat")
api.add_resource(HealthResource, "/", "/health")
api.add_resource(RegisterListResource, "/api/register/list")
api.add_resource(UserHackathonResource, "/api/user/hackathon")
api.add_resource(UserExperimentResource, "/api/user/experiment")
api.add_resource(UserExperimentListResource, "/api/user/experiment/list")

