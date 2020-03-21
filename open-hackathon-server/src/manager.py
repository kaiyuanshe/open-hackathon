# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""
from flask_script import Manager, Server, Shell

from hackathon import app
from hackathon.hmongo.database import drop_db, setup_db, add_super_user
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


manager.add_command("runserver", Server(host="0.0.0.0", port=15000, use_debugger=False))
manager.add_command("shell", Shell(banner=banner, make_context=make_shell_context))


@manager.command
def reset_db():
    drop_db()
    init_db()


@manager.command
def init_db():
    setup_db()
    # todo custom username and password
    add_super_user("admin", "admin", "admin")


if __name__ == "__main__":
    manager.run()
