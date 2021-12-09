from methods.regular.regular_api import *

import stripe

from shared.database.account.account import Account

from shared.permissions.account_permissions import Permission_Account

stripe.api_key = settings.STRIPE_API_KEY


@routes.route('/api/v1/project/<string:project_string_id>/account/billing/stripe/token',
              methods = ['POST'])
@Project_permissions.user_has_project(["admin",
                                       "Editor"])
@limiter.limit("5 per day")
def stripe_new_customer_api(project_string_id):
    spec_list = [{"account_id": int},
                 {"token": dict}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    if not settings.ALLOW_STRIPE_BILLING:
        return jsonify(log = {'error': {'ALLOW_STRIPE_BILLING': 'Not Allowed for this version'}}), 400

    with sessionMaker.session_scope() as session:
        result, log = stripe_new_customer_core(session = session,
                                               token = input['token'],
                                               account_id = input['account_id'],
                                               log = log)
        if result is False:
            return jsonify(log = log), 400

        # We should not need to do this here, but something funny
        # with account thing.
        project = Project.get(session, project_string_id)
        project.api_billing_enabled = True
        session.add(project)

        log['success'] = True
        return jsonify(log = log), 200


@Permission_Account.by_id()
def stripe_new_customer_core(session,
                             token,
                             account_id,
                             log):
    # TODO check if billing is already enabled for project?

    account = Account.get_by_id(session, account_id)

    project_list = Project.list(
        session = session,
        account_id = account.id,
        mode = "from_account_id")

    email = account.primary_user.email

    try:
        stripe_customer = stripe.Customer.create(source = token['id'],
                                                 email = email)
    except Exception as exception:
        print(exception)
        log['error']['stripe'] = "Invalid Stripe Token"
        return False, log

    session.add(account)
    account.stripe_id = stripe_customer.id
    account.payment_method_on_file = True

    # CAUTION assumes user
    user = User.get(session = session)

    # applies to many projects...
    # could also create many events instead...
    Event.new(
        kind = "billing_enabled",
        session = session,
        member_id = user.member_id,
        success = True,
        email = user.email
    )

    # Enable billing
    for project in project_list:
        # TODO this should be own function? had started a
        # billing_enable file

        session.add(project)
        project.api_billing_enabled = True

    account.credit_limit = 100 * 100  # $100

    return True, log
