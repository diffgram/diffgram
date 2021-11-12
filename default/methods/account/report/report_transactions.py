from methods.regular.regular_api import *
from shared.permissions.account_permissions import Permission_Account
from shared.database.account.transaction import Transaction
from shared.database.account.account import Account

from sqlalchemy import func
import datetime


def account_report(session,
                   account,
                   report_name):
    """


    """

    pass


# TODO get balance use account.transaction_previous.balance_new


def account_job(session,
                account,
                job):
    """
    Get all transactions for an account and job

    Relevant to both trainers and builders

    Or get specific things, ie just the amount a job cost
    so it can be a line up

    Could also use similar concepts to group charges by date?

    """

    query = session.query(Transaction.amount)

    query = query.filter(Transaction.account == account)
    query = query.filter(Transaction.job == job)

    transaction_amount_list = query.all()

    total = sum(transaction_amount_list)


@routes.route('/api/v1/account/<int:account_id>/report/transactions',
              methods = ['POST'])
@limiter.limit("20 per day")
@Permission_Account.by_id()
def account_report_transactions_api(account_id):
    spec_list = [{'date_from': str},
                 {'date_to': str}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        account = Account.get_by_id(session, account_id)

        labels, values = account_report_transactions(session = session,
                                                     account = account,
                                                     date_from = input['date_from'],
                                                     date_to = input['date_to'])

        log['success'] = True
        return jsonify(log = log,
                       labels = labels,
                       values = values), 200


def account_report_transactions(session,
                                account,
                                date_from,
                                date_to
                                ):
    """
    Grouping transactions by day?

    Different for different uses

    ie Trainer may just want to see how much money they earned

    But a project owner may want to see how much each job was costing

    And we may want to see more general stats...

    """

    # In context of a trainer

    # query = session.query(Transaction)

    date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d")
    date_to = datetime.datetime.strptime(date_to, "%Y-%m-%d")
    date_to += datetime.timedelta(days = 1)  # To "midnight"

    query = session.query(func.date_trunc('day', Transaction.time_created),
                          func.sum(Transaction.amount))

    query = query.filter(Transaction.account == account)
    query = query.filter(Transaction.time_created >= date_from)
    query = query.filter(Transaction.time_created < date_to)

    # TODO review how "time" effects this
    # ie reset date_to to be  < next day 00:00
    # and maybe check date_from is set to 00:00?
    # datetime.timedelta(days=1)

    # Group by day
    query = query.group_by(func.date_trunc('day', Transaction.time_created))

    query = query.order_by(func.date_trunc('day', Transaction.time_created))

    list_by_period = query.all()

    with_missing_dates = Stats.fill_missing_dates(date_from = date_from,
                                                  date_to = date_to,
                                                  list_by_period = list_by_period)

    # can show on chart...

    labels, values = zip(*with_missing_dates)

    return labels, values
