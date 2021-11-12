import shared.database_setup_supporting
from default.methods.regular.regular_api import *

from default.methods.account.plan.usage_cycle import Usage
from shared.database.account.plan import Plan
from shared.database.account.account import Account

from default.methods.account.billing.billing_stripe_charge import stripe_customer_charge_core

with sessionMaker.session_scope() as session:
    # usage = Usage(session = session)

    # project_string_id = "bourgault_trashflow"
    # project_string_id = "product_selection"
    # project_string_id = "fs_digital_empties"

    project = Project.get(
        session = session,
        project_string_id = project_string_id
    )

    print(project.account_id)

    stripe_customer_charge_core(
        session = session,
        account_id = project.account_id)
