# Acrobatics for testing vs / normal setup.
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

import stripe

from shared.database.user import User
from shared.database.project import Project
from shared.database.account.account import Account
from shared.database.account.transaction import Transaction

from shared.permissions.account_permissions import Permission_Account

stripe.api_key = settings.STRIPE_API_KEY

# Not enabled yet
"""
@routes.route('/api/v1/account/billing/stripe/charge',
			  methods = ['POST'])
@limiter.limit("5 per day")
def stripe_customer_charge_api():

	spec_list = [{"account_id": int}]

	log, input, untrusted_input = regular_input.master(request=request,
													   spec_list=spec_list)
	if len(log["error"].keys()) >= 1:
		return jsonify(log=log), 400


	with sessionMaker.session_scope() as session:

		result = stripe_customer_charge_permissions_check(
						session = session,
						account_id = input['account_id'])

		log['success'] = True
		return jsonify(log=log), 200
"""


@Permission_Account.by_id()
def stripe_customer_charge_permissions_check(
    session,
    account_id):
    # permission check for web
    # so we can still core stripe_customer_charge_core() internally for testing
    # probably a better way...

    return stripe_customer_charge_core(
        session,
        account_id)


def stripe_customer_charge_core(session,
                                account_id):
    account = Account.get_by_id(session, account_id)

    # TODO what other checks here?
    # ie is positive value ...
    amount = account.transaction_previous.balance_new

    # WIP for manual amount
    # amount = 1

    currency = 'usd'
    description = "Diffgram Service"

    customer_id = account.stripe_id

    # TEST CUSTOMER ID
    # Needs to also be usine test key
    # customer_id = "cus_EOMzKGWK9RRLH0"

    customer = stripe.Customer.retrieve(customer_id)

    if amount > 50000:  # $500
        return False

    stripe_charge_result = stripe.Charge.create(
        source = customer.default_source,
        customer = customer_id,
        amount = amount,
        currency = currency,
        description = description,
        receipt_email = account.primary_user.email
    )

    transaction = Transaction.new(session = session,
                                  account = account,
                                  transaction_type = "payment",
                                  amount = -amount,
                                  audit_cache = stripe_charge_result
                                  )

    return True
