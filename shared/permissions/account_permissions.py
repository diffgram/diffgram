from functools import wraps

from shared.database.user import User
from shared.database.project import Project
from shared.database.auth.api import Auth_api

from shared.database.account.account import Account

from werkzeug.exceptions import Forbidden
from shared.helpers.permissions import getUserID
from shared.helpers import sessionMaker

from flask import request


class Permission_Account():
    def by_id():
        """
        Defaults to forbidden if no match found


       """

        def wrapper(func):
            @wraps(func)
            def inner(*args, **kwds):

                account_id = kwds.get('account_id', None)

                if account_id is None or account_id in ["null", "undefined"]:
                    raise Forbidden("No access.")

                with sessionMaker.session_scope() as session:

                    result = Permission_Account.permissions(session = session,
                                                            account_id = account_id)

                    if result is True:
                        return func(*args, **kwds)

                raise Forbidden("No access.")

            return inner

        return wrapper

    def permissions(session,
                    account_id):
        # TODO handle for API member calls
        account = Account.get_by_id(session = session,
                                    account_id = account_id)
        if account is None:
            raise Forbidden("No access.")

        # TODO review
        user_id = getUserID()
        if user_id is None:
            raise Forbidden("Please login.")

        user = User.get_by_id(session = session,
                              user_id = user_id)

        if user.is_super_admin == True:
            return True

        if account.primary_user == user:
            return True
