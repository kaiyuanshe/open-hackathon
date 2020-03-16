# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""
from flask_script import Manager, Server, Shell

from hackathon import app
from hackathon.hmongo import drop_db
from hackathon.hmongo.models import User

banner = r"""
 _____                          __  __                   __                __    __                         
/\  __`\                       /\ \/\ \                 /\ \              /\ \__/\ \                        
\ \ \/\ \  _____      __    ___\ \ \_\ \     __      ___\ \ \/'\      __  \ \ ,_\ \ \___     ___     ___    
 \ \ \ \ \/\ '__`\  /'__`\/' _ `\ \  _  \  /'__`\   /'___\ \ , <    /'__`\ \ \ \/\ \  _ `\  / __`\ /' _ `\  
  \ \ \_\ \ \ \L\ \/\  __//\ \/\ \ \ \ \ \/\ \L\.\_/\ \__/\ \ \\`\ /\ \L\.\_\ \ \_\ \ \ \ \/\ \L\ \/\ \/\ \ 
   \ \_____\ \ ,__/\ \____\ \_\ \_\ \_\ \_\ \__/.\_\ \____\\ \_\ \_\ \__/.\_\\ \__\\ \_\ \_\ \____/\ \_\ \_\
    \/_____/\ \ \/  \/____/\/_/\/_/\/_/\/_/\/__/\/_/\/____/ \/_/\/_/\/__/\/_/ \/__/ \/_/\/_/\/___/  \/_/\/_/
             \ \_\                                                                                          
              \/_/                                                                                          
"""

manager = Manager(app)


def make_shell_context():
    return {
        "app": app,
    }


manager.add_command("runserver", Server(host="0.0.0.0", port=15000, use_debugger=True))
manager.add_command("shell", Shell(banner=banner, make_context=make_shell_context))


@manager.command
def reset_db():
    drop_db()
    setup_db()


@manager.command
def setup_db():
    """Initialize db tables

    make sure database and user correctly created in db
    in case upgrade the table structure, the origin table need be dropped firstly
    """
    # init REQUIRED db data.

    # reserved user is deleted, may not need in mongodb implementation

    # default super admin

    admin = User(
        name="admin",
        nickname="admin",
        password="e8104164dfc4a479e42a9f6c0aefd2be",
        avatar_url="/static/pic/monkey-32-32px.png",
        is_super=True)

    User.objects(name="admin").update_one(__raw__={"$set": admin.to_mongo().to_dict()}, upsert=True)


if __name__ == "__main__":
    manager.run()
