from methods.regular.regular_api import *

from shared.database.user import User
from shared.database.account.account import Account


@routes.route('/api/v1/account/list',
              methods = ['POST'])
@limiter.limit("20 per day")
def account_report_info_api():
    spec_list = [
        {'mode_trainer_or_builder': str},
        {'primary_email': None}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        user = User.get(session)

        # account_type = "billing" # default for now, could use this to check usage too
        account_type = None  # get all accounts

        user_id = user.id

        primary_email = None
        if input['primary_email']:

            if user.is_super_admin is not True:
                log['error']['permission'] = "Invalid permission."
                return jsonify(log = log), 400

            primary_email = input['primary_email']

            if primary_email:
                user = User.get_by_email(session, primary_email)

                if not user:
                    log['error']['email'] = "No such user."
                    return jsonify(log = log), 400

                user_id = user.id

            # Clear as work around
            # since Account.get_list() expects only one to fire
            # see TODO about maybe making too functions for this

        account_list = Account.get_list(session = session,
                                        user_id = user_id,
                                        mode_trainer_or_builder = input['mode_trainer_or_builder'],
                                        account_type = account_type,
                                        by_primary_user = True
                                        )

        account_list_serialized = []

        # List vs not list thing not quite right here yet

        for account in account_list:
            account_list_serialized.append(account.serialize())

        log['success'] = True
        return jsonify(log = log,
                       account_list = account_list_serialized), 200
