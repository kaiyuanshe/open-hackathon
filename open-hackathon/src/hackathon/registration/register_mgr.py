import sys

sys.path.append("..")
from hackathon.database.models import *
from hackathon.database import db_adapter
from datetime import datetime
from hackathon.log import log
from flask import g


class RegisterManger(object):
    def get_register_list(self):
        # TODO make query result with pagination
        registers = db_adapter.find_all_objects(Register, Register.hackathon_id == g.hackathon_id)
        return map(lambda u: u.json(), registers)


    def get_register_by_id(self, **args):
        if "id" not in args:
            return {"error": "Bad request"}, 400
        register = db_adapter.find_first_object(Register, Register.id == args['id'])
        if register is not None:
            return register.json()
        else:
            return {"error": "REGISTER NOT FOUND"}, 400


    def create_or_update_register(self, **args):
        try:
            register = db_adapter.find_first_object(Register,Register.email==args['email'],Register.hackathon_id==g.hackathon_id)
            if register is None:
                #create a register
                log.debug("create a new register")
                db_adapter.add_object_kwargs(Register,
                                             register_name=args['name'],
                                             email=args['email'],
                                             create_time=datetime.utcnow(),
                                             description=args['description'],
                                             enabled=1,  # 0: disabled 1:enabled
                                             jstrom_api='',
                                             jstrom_mgmt_portal='',
                                             hackathon_id=g.hackathon_id)
            else:
                #update a aready existe register
                log.debug("update a new register")
                db_adapter.update_object(register,
                                         register_name=args['name'],
                                         email=args['email'],
                                         create_time=datetime.utcnow(),
                                         description=args['description'],
                                         enabled=args['enabled'],  # 0: disabled 1:enabled
                                         strom_api='',
                                         jstrom_mgmt_portal='',
                                         hackathon_id=g.hackathon_id)
        except Exception:
            log.error("create or update register faild")
            return {"error": "INTERNAL SERVER ERROR"}, 500


    def delete_register(self, **args):
        if args['id'] is None:
            return {"error": "Bad request"}, 400
        try:
            register = db_adapter.find_first_object(Register, Register.id == args['id'])
            if register is None:
                return {"message": "already removed"}, 200
            db_adapter.delete_object(register)
        except Exception:
            log.error("delete register faild")
            return {"error": "INTERNAL SERVER ERROR"}, 500


register_manager = RegisterManger()