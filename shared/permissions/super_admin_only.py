# OPENCORE - ADD
from functools import wraps

from shared.database.user import User

from werkzeug.exceptions import Forbidden, Unauthorized
from shared.helpers.permissions import getUserID
from shared.helpers.permissions import LoggedIn
from shared.helpers.permissions import defaultRedirect
from shared.helpers import sessionMaker

from flask import request


class Super_Admin():

    @staticmethod
    def is_super(allow_support=False):
        """
        Must be super admin

       """

        def wrapper(func):
            @wraps(func)
            def inner(*args, **kwds):

                with sessionMaker.session_scope() as session:

                    if LoggedIn() != True:
                        raise Unauthorized("No access.")

                    user = session.query(User).filter(User.id == getUserID(session = session)).first()

                    if user is None:
                        raise Unauthorized("No access.")

                    if allow_support is True:
                        if user.is_support_user() is True:
                            return func(*args, **kwds)

                    if user.is_super_admin == True:
                        return func(*args, **kwds)
                    else:
                        raise Forbidden("No access.")

                raise Forbidden("No access.")

            return inner

        return wrapper
