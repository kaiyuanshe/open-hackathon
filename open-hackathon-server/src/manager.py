# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""
from flask_script import Manager, Server, Shell

from hackathon import app
from hackathon.hmongo.database import drop_db, setup_db, add_super_user

import click

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
    click.confirm('This operation will delete the database, do you want to continue?', abort=True)
    drop_db()
    setup_db()
    click.echo('Success reset database.')
    click.echo('Success Add A New Admin Count. (admin@admin)')


@manager.command
def init_db():
    setup_db()
    click.echo('Success init database.')
    click.echo('Success Add A New Admin Count. (admin@admin)')


@manager.command
def create_super_user(username, password):
    add_super_user(username, username, password)
    click.echo('Success Add A Super Count. ({0}@{1})'.format(username, password))

@manager.command
def create_test_user(username, password):
    add_super_user(username, username, password, is_super=False)
    click.echo('Success Add A Test Count. ({0}@{1})'.format(username, password))

if __name__ == "__main__":
    manager.run()
