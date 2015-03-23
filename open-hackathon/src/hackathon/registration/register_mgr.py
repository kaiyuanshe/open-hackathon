import sys

sys.path.append("..")
from hackathon.database.models import *
from hackathon.database import db_adapter
from datetime import datetime
from hackathon.log import log



class RegisterManger(object):

    def get_register_list(self,hackathon_id):
        #TODO make query result with pagination
        registers = db_adapter.find_all_objects(Register,Register.hackathon_id==hackathon_id)
        return map(lambda u: u.json(),registers)


    def get_one_register(self,*args):
        if args['id'] is None:
            return {"error": "Bad request"}, 400
        register = db_adapter.find_first_object(Register, Register.id == args['id'])
        return register.json()


    def create_register(self,**args):
        #create a new Register for a hackathon
        try:
            db_adapter.add_object_kwargs(Register,
                                        register_name = args['name'],
                                        email = args['email'],
                                        create_time = datetime.utcnow(),
                                        description = args['description'],
                                        enabled = 1,  # 0: disabled 1:enabled
                                        jstrom_api = '',
                                        jstrom_mgmt_portal = '',
                                        hackathon_id = args['hackathon_id'])
            db_adapter.commit()
        except Exception:
            log.error("create register faild")
            return {"error": "INTERNAL SERVER ERROR"}, 500


    def update_register(self,**args):
        #update a Register
        if args['id'] is None:
            return {"error": "Bad request"}, 400
        try:
            register = db_adapter.find_first_object(Register, Register.id==args['id'])
            db_adapter.update_object(register,
                                        register_name = args['name'],
                                        email = args['email'],
                                        create_time = datetime.utcnow(),
                                        description = args['description'],
                                        enabled = args['enabled'],  # 0: disabled 1:enabled
                                        strom_api = '',
                                        jstrom_mgmt_portal = '',
                                        hackathon_id = args['hackathon_id'])
            db_adapter.commit()
        except Exception:
            log.error("update register faild")
            return {"error": "INTERNAL SERVER ERROR"}, 500


    def delete_register(self,**args):
        if args['id'] is None:
            return {"error": "Bad request"}, 400
        try:
            register = db_adapter.find_first_object(Register, Register.id == args['id'])
            db_adapter.delete_object(register)
        except Exception:
            log.error("delete register faild")
            return {"error": "INTERNAL SERVER ERROR"}, 500


register_manager = RegisterManger()