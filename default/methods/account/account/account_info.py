from methods.regular.regular_api import *
from shared.database.user import User
from shared.database.account.account import Account

@routes.route('/api/v1/account/list', methods=['POST'])
@limiter.limit("20 per day")
def account_report_info_api() -> tuple:
    """
    Get a list of accounts for a user.
    """
    spec_list = [
        {'mode_trainer_or_builder': str},
        {'primary_email': (str, None)}
    ]

    log, input, untrusted_input = regular_input.master(request=request, spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        user = User.get(session)

        if not user:
            log["error"]["user"] = "No such user."
            return jsonify(log=log), 400

        account_type = None  # get all accounts
        user_id = user.id

        if input.get('primary_email'):
            if user.is_super_admin is not True:
                log["error"]["permission"] = "Invalid permission."
                return jsonify(log=log), 400

            primary_email = input['primary_email']

            if not primary_email:
                log["error"]["email"] = "Email cannot be empty."
                return jsonify(log=log), 400

            user = User.get_by_email(session, primary_email)

            if not user:
                log["error"]["email"] = "No such user."
                return jsonify(log=log), 400

            user_id = user.id

        account_list = Account.get_list(session=session, user_id=user_id, mode_trainer_or_builder=input['mode_trainer_or_builder'], account_type=account_type, by_primary_user=True)

        account_list_serialized = [account.serialize() for account in account_list]

        log['success'] = True
        return jsonify(log=log, account_list=account_list_serialized), 200
