### LEGACY

import shared.database_setup_supporting
from default.methods.regular.regular_api import *

from default.methods.account.plan.usage_cycle import Usage
from shared.database.account.plan import Plan
from shared.database.account.account import Account


def run_count_criteria(session, project_string_id):
    usage = Usage(session = session)

    project = Project.get(
        session = session,
        project_string_id = project_string_id
    )

    usage.project = project

    # print(project.account_id, project.plan_id)

    # project_list = Account.project_list(
    #		session = session,
    #		account_id = account.id)

    project_list = Project.list_from_plan(
        session = session,
        plan = project.plan)

    print("Projects", project_list)

    # usage.mode = "active_not_newly_created"
    # print(usage.mode)

    # usage.setup_conditions_and_dates_from_mode()

    # usage.determine_billable_directory_file_and_instance()

    # usage.instance_usage_transaction_new()

    # This type of report gives it by day
    # BUT recall it's the ACTIVE during that time... not created...
    # So we are recording ACTIVE instances for that day
    # BUT could use somthing like this to re run it...
    # Maybe should just declare start day, and then setup_conditions
    # takes care of rest?
    # ie I want to bill for day x, and then it handles all that

    # Manually set
    """
    account_id = 417

    usage.billing_account = Account.get_by_id(	
            session, 
            account_id)
    """
    # OR from project
    usage.billing_account = project.account

    # Must start with 1

    # MUST CHANGE DATE TOO
    for i in range(28, 29):

        # usage.date_from = datetime.datetime(2019, 5, i)

        for project in project_list:

            print("\n\n")
            if project.deletion_pending:
                print(project.name, "deletion_pending", project.deletion_pending)

                # Not charging for this by default
                # But need to have better controls here...
                continue

            print(project.name)

            # never need to set date from
            # Becuase that's always set by system
            # usage.date_from = None

            # CAREFUL MUST CHANGE range date too to get date right!!!!
            usage.date_to = datetime.datetime(2019, 9, i)

            usage.project = project

            # TODO clarify this is the instance billing usage account
            account = usage.get_acount()

            """
            usage.mode = "newly_created"
            print(usage.mode)
            usage.setup_conditions_and_dates_from_mode()

            usage.determine_billable_directory_file_and_instance()

            usage.instance_usage_transaction_new()
            """

            usage.mode = "active_not_newly_created"
            print(usage.mode)

            usage.setup_conditions_and_dates_from_mode()

            usage.use_cache = True

            usage.determine_billable_directory_file_and_instance()

            # CAREFUL always run the above first without this
            # to make sure it's right, it's hard to fix transactions afterwards
            # because they are linked to each other so have to say manually set to 0... sigh
            usage.instance_usage_transaction_new()

            # Caution this is not looking at existing transactions
            # but pulling from object ie determine_billable_directory_file_and_instance
            usage.billing_transaction_new()


# print(usage.log)


def run_billing_transaction_on_instance_usage(session):
    usage = Usage(session = session)

    project_string_id = "obstacle-module"

    project = Project.get(
        session = session,
        project_string_id = project_string_id)

    usage.project = project

    usage.billing_transaction_new()


def run_usage_transaction(session):
    usage = Usage(session = session)

    project_string_id = "ki67_smallcrops"

    project = Project.get(
        session = session,
        project_string_id = project_string_id)

    """
    usage.usage_update(
        instances_count,
        instance_list,
        project
        )

    # GAH this feels so awakard
    plan = Plan.get_by_id(
        session = session,
        plan_id = 5)

    plan = project.plan

    user = project.user_primary

    account_list = Account.get_list( 
                        session = session,
                        user_id = user.id,
                        mode_trainer_or_builder = "builder",
                        account_type = "billing",
                        by_primary_user = True)

    account = account_list[0]
    """

    account = project.account

    # usage.plan_usage(plan = plan)

    usage.billing_charge_base_cost(
        plan,
        account
    )


# usage.project_usage(project = project)


def billing_charge_base_cost(
    session,
    project_string_id):
    usage = Usage(session = session)

    # project_string_id = "cam2_video1"
    # project_string_id = "digital_empties"

    project = Project.get(
        session = session,
        project_string_id = project_string_id
    )

    plan = project.plan
    account = project.account

    usage.billing_charge_base_cost(
        plan,
        account
    )


def reset_payment_method(
    session,
    project_string_id):
    project = Project.get(
        session = session,
        project_string_id = project_string_id
    )

    # account = project.account

    # account = Account.get_by_id(
    #	session,
    #	1)

    print(account.payment_method_on_file)

    session.add(account)
    account.payment_method_on_file = False


with sessionMaker.session_scope() as session:
    project_string_id = "fs_digital_empties"
    # project_string_id = "product_selection"
    # project_string_id = "bourgault_trashflow"

    run_count_criteria(session, project_string_id)

# billing_charge_base_cost(session,project_string_id)

# reset_payment_method(session, project_string_id)
