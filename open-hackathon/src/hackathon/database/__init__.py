import sys

sys.path.append("..")
from hackathon.constants import ROLE
from flask_sqlalchemy import SQLAlchemy
from hackathon import app
from db_adapters import SQLAlchemyAdapter

db = SQLAlchemy(app)
db_adapter = SQLAlchemyAdapter(db)


class UserMixin(object):
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_user_id(self):
        pass

    def get_id(self):
        return unicode(self.get_user_id())

    def is_admin(self):
        return self.has_roles(ROLE.ADMIN)

    def has_roles(self, *requirements):
        """ Return True if the user has all of the specified roles. Return False otherwise.
            has_roles() accepts a list of requirements:
                has_role(requirement1, requirement2, requirement3).
            Each requirement is either a role_name, or a tuple_of_role_names.
                role_name example:   'manager'
                tuple_of_role_names: ('funny', 'witty', 'hilarious')
            A role_name-requirement is accepted when the user has this role.
            A tuple_of_role_names-requirement is accepted when the user has ONE of these roles.
            has_roles() returns true if ALL of the requirements have been accepted.
            For example:
                has_roles('a', ['b', 'c'], d)
            Translates to:
                User has role 'a' AND (role 'b' OR role 'c') AND role 'd'"""

        # Allow developers to attach the Roles to the User or the UserProfile object
        if hasattr(self, 'roles'):
            user_roles = self.roles
        else:
            user_roles = None
        if not user_roles:
            return False

        # Translates a list of role objects to a list of role_names
        user_role_names = [user_role.role.name for user_role in user_roles]

        # has_role() accepts a list of requirements
        for requirement in requirements:
            if isinstance(requirement, (list, tuple)):
                # this is a tuple_of_role_names requirement
                tuple_of_role_names = requirement
                authorized = False
                for role_name in tuple_of_role_names:
                    if role_name in user_role_names:
                        # tuple_of_role_names requirement was met: break out of loop
                        authorized = True
                        break
                if not authorized:
                    return False  # tuple_of_role_names requirement failed: return False
            else:
                # this is a role_name requirement
                role_name = requirement
                # the user must have this role
                if not role_name in user_role_names:
                    return False  # role_name requirement failed: return False

        # All requirements have been met: return True
        return True

