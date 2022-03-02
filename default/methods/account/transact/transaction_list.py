from methods.regular.regular_api import *

from shared.database.project import Project
from shared.database.user import User
from shared.database.task.job.job import Job
from shared.database.task.job.user_to_job import User_To_Job
from shared.database.task.credential.credential import Credential
from shared.database.task.credential.credential_type_to_job import Credential_Type_To_Job
from shared.database.account.transaction import Transaction

from shared.permissions.account_permissions import Permission_Account

from sqlalchemy import func

import datetime


@routes.route('/api/v1/transaction/list',
              methods = ['POST'])
def transaction_list_api():
    spec_list = [{'date_from': None},
                 {'date_to': None},
                 {'status': None},
                 {'account_id': str},
                 {'job_id': None},
                 {'mode_data': str}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        transaction_list = transaction_list_core(session = session,
                                                 date_from = input['date_from'],
                                                 date_to = input['date_to'],
                                                 status = input['status'],
                                                 job_id = input['job_id'],
                                                 account_id = input['account_id'])

        log['success'] = True
        return jsonify(log = log,
                       transaction_list = transaction_list), 200


@Permission_Account.by_id()
def transaction_list_core(session,
                          date_from,
                          date_to,
                          status,
                          job_id,
                          account_id):
    # if using time created

    # TODO handle if account id is null
    # don't want to just reject as we may want to view multiple accounts at once
    # ie a mode

    query = session.query(Transaction)

    if account_id:
        query = query.filter(Transaction.account_id == account_id)

    if date_from:
        date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d")
        date_to = datetime.datetime.strptime(date_to, "%Y-%m-%d")
        date_to += datetime.timedelta(days = 1)

        query = query.filter(Transaction.time_created >= date_from)
        query = query.filter(Transaction.time_created < date_to)

    if status:
        if status != "all":
            query = query.filter(Transaction.status == status)

    if job_id:
        query = query.filter(Transaction.job_id == job_id)

    query = query.order_by(Transaction.time_created.desc())

    transaction_list = query.all()

    out_list = []

    for transaction in transaction_list:
        # TODO get builder vs trainer mode
        out_list.append(transaction.serialize_for_list_view_builder())

    return out_list
