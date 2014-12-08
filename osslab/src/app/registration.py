from database import *


class Registration:

    def get_by_email(self, email):
        return Register.query.filter_by(email=email).first()

    #get all register names and their status from register table, return value is list and list's value is tuple, [(register_name, online_status, submitted_status)]
    def get_register_name_status(self):
        return Register.query.with_entities(Register.register_name, Register.online, Register.submitted).all()

    #get a register's online status
    def get_register_online_status(self, registername):
        u = Register.query.filter_by(register_name = registername).first()
        return u.online

    #get a register's submitted status
    def get_register_submitted_status(self, registername):
        u = Register.query.filter_by(register_name = registername).first()
        return u.submitted

    #set a register's online status
    def set_online_status(self, registername, online_status):
        u = Register.query.filter_by(register_name = registername).first()
        u.online = online_status
        db.session.commit()

    #set a register's submitted status
    def set_submitted_status(self, registername, submitted_status):
        u = Register.query.filter_by(register_name = registername).first()
        u.online = submitted_status
        db.session.commit()




