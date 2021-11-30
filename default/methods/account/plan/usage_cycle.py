### LEGACY


try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

from shared.database.account.account import Account
from shared.database.account.transaction import Transaction
from shared.database.account.plan import Plan


class Usage():
    """

    Design doc

    https://docs.google.com/document/d/1Tc9JZL_zaqTfmp6zlCaBuNX9h4mK6XRxSqgqq73mDhE

    """

    def __init__(
        self,
        session):

        self.log = {}
        self.session = session

    def usage_diffgram_plans(
        self):
        """

        Main entry point

        Check usage critera accross all plans?
        This is the master "cordinator" ie diffgram level

        We start with plans, becuase project limits get grouped by plan?

        """

        with sessionMaker.session_scope() as self.session:
            plan_list = Plan.list(session = self.session)

            for plan in plan_list:
                self.plan_usage(plan = plan)

    # TODO overall usage cycle reporting here
    # ie who got charged what

    def plan_usage(
        self,
        plan):
        """
        Get all projects attached to a plan
        Update usage
        Update billing


        plan, db Plan object


        """

        project_list = Plan.project_list_from_plan(
            session = self.session,
            plan = plan)

        for project in project_list:
            self.project_usage(project)

        # TODO pass data here as needed.

        self.billing_transaction_new()

    # TODO final plan reporting here?

    def project_usage(
        self,
        project):
        """
        Update a single project for usage

        checks count critiera

        does usage transactions as appropriate

        Returns info to do billing transactions as required

        """

        # TODO this is old?

        self.log[project.id] = {}

        instances_count, instance_list = self.count_criteria(
            project = project)

        self.usage_transaction_new(
            amount = instances_count,
            instance_list = instance_list,
            project = project
        )

    def get_acount(
        self):

        # assumes user is project primary
        user = self.project.user_primary

        account_list = Account.get_list(
            session = self.session,
            user_id = user.id,
            mode_trainer_or_builder = "builder",
            account_type = "instance_usage",
            by_primary_user = True)

        if len(account_list) == 0:  # or if not account_list...

            # Create a new account if no account
            account = Account.account_new_core(
                session = self.session,
                primary_user = user,
                mode_trainer_or_builder = "builder",
                account_type = "instance_usage",
                nickname = "Instance Usage Account")

        else:
            account = account_list[0]  # not a fan of this

        self.account = account
        return account

    # OLD
    def create_period_dates(
        self,
        mode,
        account
    ):

        if mode == "newly_created":
            # Server is in different time stamp apparently
            # Shouldn't need this + datetime thing
            date_to = datetime.datetime.now() + datetime.timedelta(days = 1)

            # TODO not clear right format to store datetime object in log
            # Want it to be human readable for debugging, ie looking at it quickly
            # and see it's the right date. Made a slight error in though process
            # as misread which was which

            # TODO log properly which method is being used here since
            # this could be very key

            # TODO determine correct "cycle" concept, so even if it's by day
            # it's by day for say midnight to midnight? or something like that?
            # not sure if we want it to be so arbitrary

            # Determine usage cycle
            """
            if account.transaction_previous:
                # We don't need to subtract from "now" since 
                # This is already the exact datetime object we want to start from
                date_from = account.transaction_previous.time_created
            """

        return

    def setup_conditions_and_dates_from_mode(
        self
    ):
        """
        Sets up conditions for search

        Define newly created as within the last x period.
        Active not newly created is then UP TO x period.

        """

        # How are we handling the overlap between these two?
        # Still feels unclear
        # I guess you could do it by dates right? so
        # for a given cycle date, the active not newly created
        # the date_to starts 30 days in past?

        if self.mode == "active_not_newly_created":
            self.exclude_removed = True

            # This is always the cycle date
            # self.date_to = datetime.datetime.now() - datetime.timedelta(days=1)

            # If we are also using newly created...
            # self.date_to = self.date_to - datetime.timedelta(days=30)

            # This is always None, since this is all active
            self.date_from = None

        if self.mode == "newly_created":
            self.exclude_removed = False

            # This is always the cycle date
            # self.date_to = datetime.datetime.now() + datetime.timedelta(days=1)

            # And this is always 30 days prior, since that's the period
            # In which we must count an instance
            self.date_from = self.date_to - datetime.timedelta(days = 30)

        #  + datetime.timedelta(days=1) is just for difference server vs local
        # and then date_from has a delta of 2 days intsead of one

    def determine_billable_directory_file_and_instance(
        self
    ):
        """
        This is focused on excuting the search given the various conditions

        self.project, class Project object
        account, class Account object

        Count how many of x? object
        Focused on instances for now

        Maybe want to move discussion to design doc here

        How are we tracking predicions that don't create files
        for instances here...

        Prob want to use created_time both ways so that's the same right?

        All three need to be here since exclude_removed effects all 3

        """

        # WIP

        # This is how we are doing it for ml projects but
        # relys on the boxes_count (instance_count) to be accurate
        # Could refresh this
        # or could construct a more complex sub query that attachs instance
        # directly?

        # Different queries for different file types??

        # TODO only doing created since time of last transaction right?

        # So isn't coupled directly to self.project_usage running?
        # Not clear much point of this though since we need amount and instance_list...
        start_time = time.time()

        if not self.log.get(self.project.id):
            self.log[self.project.id] = {}

        # Need to get account here since we use the previous transaction for the previous time check.

        print("datetime_from \t", str(self.date_from))
        print("datetime_to \t", str(self.date_to))

        self.log[self.project.id]['date_from'] = self.date_from
        self.log[self.project.id]['date_to'] = self.date_to

        directory_list = WorkingDir.list(
            session = self.session,
            project_id = self.project.id,
            exclude_archived = self.exclude_removed
        )
        # Handle all directories in project
        # print(directory_list)
        self.log[self.project.id]['directory_list'] = [directory.id for directory in directory_list]

        # Default query here excludes File.state == 'removed'.
        file_list = WorkingDirFileLink.file_list(
            session = self.session,
            directory_list = directory_list,
            type = "image",
            time_kind = "created",
            exclude_removed = self.exclude_removed,
            limit = None,
            date_from = self.date_from,
            date_to = self.date_to
        )

        print("len file list", len(file_list))

        # instances_count_list = []
        self.instance_list = []
        self.instance_list_count = 0

        if self.use_cache is None:
            self.use_cache = True

        for file in file_list:

            # TODO proper query and only need ids here?

            # new_instance_list = []

            if self.use_cache is True:
                if file.count_instances_changed:
                    self.instance_list_count += file.count_instances_changed

            # HUGE time difference
            # and this is only needed really if we
            # are worring about deleted (which shou

            # TODO next step
            # Update count_instance_changed using this if needed
            # And figure out where it's not updating it properly
            # (that way don't have to keep re running this.)

            if self.use_cache is False:
                self.instance_list_count += Instance.list(
                    session = self.session,
                    file_id = file.id,
                    exclude_removed = self.exclude_removed,
                    date_from = self.date_from,
                    date_to = self.date_to,
                    return_kind = "count"
                )

        # self.instance_list.extend(new_instance_list)

        # self.instance_list_count = len(self.instance_list)

        print("Instance count", self.instance_list_count)
        print("Ran in", time.time() - start_time)

        self.sum_usage_count = self.instance_list_count

    # WIP

    # Two types of transactions
    # Usage and billing

    #

    def instance_usage_transaction_new(
        self
    ):
        """
        This is just straight recording usage, not worrying
        about which is which here?

        How we are getting the account, if we know the project should be able to pull
        from that instead of Account.get_list()

        """
        amount = self.instance_list_count
        sub_kind = self.mode

        if amount <= 0:
            self.log[self.project.id]['amount'] = str(amount)
            self.log[self.project.id]['info'] = "No usage to create."
            return

        audit_cache = {}

        # For performance only do newly created

        """
        if self.mode == "newly_created":

            instance_list = []
            for instance in self.instance_list:

                # TODO instance.created_time to a year/month/date only?

                if instance.created_time == self.date_to:
                    instance_list.append(instance.id)

            audit_cache['instance_id_list'] = instance_list
        """

        transaction_builder = Transaction.new(session = self.session,
                                              account = self.account,
                                              transaction_type = "instance_usage",
                                              sub_kind = sub_kind,
                                              amount = amount,
                                              audit_cache = audit_cache,
                                              time_created = self.date_to,
                                              project_id = self.project.id
                                              )

        self.log[self.project.id]['info'] = "Did a transaction"
        self.log[self.project.id]['transaction_id'] = transaction_builder.id

        self.try_to_commit()

    def try_to_commit(self):

        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise

    def billing_transaction_new(self):
        """
        determine
        Do billing

        For every batch of 1000?

        If over threshold
        If billing cycle passed

        """
        audit_cache = {}

        sum_usage_count = self.sum_usage_count
        audit_cache['usage_count'] = sum_usage_count

        # This is sorta time since last bill? ie 30 days?
        in_unbilled_cycle = False

        # TODO handle if not project id / attach
        # this log to project id?

        if sum_usage_count == 0:
            # self.log['billing_transaction'] == "No usage to bill"
            print("No usage to bill")
            return

        # Not using this until we have stronger concept
        # of a "cycle"

        # and in_unbilled_cycle is False:

        if sum_usage_count < 100:
            self.log['info'] = "Not enough instances or time to bill"
            print("Not enough instances or time to bill")
            return

        # unit is a billable group of 1000 (or "tier")
        units = sum_usage_count // 1000

        # // (Floor) operation will ignore hundreds place here
        # So 564 // 1000 == 0    1,564 // 1000 == 1 etc.
        units += 1
        audit_cache['units'] = units

        # $9 / 30  expressed in integer terms where 100 == $1.00

        # DAILY
        rate = 30
        # audit_cache['daily_rate'] = rate

        # MONTHLY
        rate = 900  # $9.00
        audit_cache['monthly_rate'] = rate

        # Assumed to always be whole numbers
        amount = units * rate

        print("Charging", amount)

        # other checks?
        # now assume we are doing a billing transaction?

        # TODO get account from project?

        # account = None

        # TODO calculate amount based on plan rate
        # and sum_usage

        """
        account_list = Account.get_list( 
            session = self.session,
            user_id = user.id,
            mode_trainer_or_builder = "builder",
            account_type = "billing",
            by_primary_user = True)
        """

        transaction = Transaction.new(
            session = self.session,
            account = self.billing_account,
            transaction_type = "billing",
            sub_kind = "instance_usage",
            audit_cache = audit_cache,
            amount = amount,
            time_created = self.date_to,
            project_id = self.project.id
        )

        # log['info'] = "Did a transaction"
        self.try_to_commit()

    def billing_charge_base_cost(
        self,
        plan,
        account
    ):

        # TODO get most recent billing_cost_monthly
        # Check date?
        # If date then do that transaction
        # OR some better way to see if it has been charged?
        # OR should we define some type of a "cycle day" on the plan?
        # And then just charge it on the cycle day?
        # ie a plan created on day 1 of month has a cycle of 1
        # so then it just checks if cycle is ==.
        # Then maybe does the transaction check AFTER just to be safe?

        cost_monthly = plan.template.cost_monthly

        print("Monthly cost", cost_monthly)

        transaction = Transaction.new(
            session = self.session,
            account = account,
            transaction_type = "billing_cost_monthly",
            amount = cost_monthly)

    def manual_transaction(
        account,
        transaction_type,
        amount
    ):

        # WORK IN PROGRESS

        transaction = Transaction.new(
            session = self.session,
            account = account,
            transaction_type = "billing_cost_monthly",
            amount = cost_monthly)
