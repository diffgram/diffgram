from methods.regular.regular_api import *
from shared.database.task.task import Task

from sqlalchemy import func

import datetime


@routes.route('/api/v1/diffgram/stats/leaderboard',
              methods = ['POST'])
@General_permissions.grant_permission_for(Roles = [])  # Super admin allowed by default
@limiter.limit("20 per day")
def stats_leadboard_api():
    spec_list = [{'date_from': str},
                 {'date_to': str},
                 {'status': str}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        labels, values = stats_leaderboard_core(session = session,
                                                date_from = input['date_from'],
                                                date_to = input['date_to'],
                                                status = input['status'])

        log['success'] = True
        return jsonify(log = log,
                       labels = labels,
                       values = values), 200


# would need to cache this too

def stats_leaderboard_core(session,
                           date_from,
                           date_to,
                           status = "completed"):
    # if using time created

    query = session.query(Task.assignee_user_id,
                          func.count(Task.id))

    query = query.filter(Task.time_created >= date_from)
    query = query.filter(Task.time_created <= date_to)

    query = query.filter(Task.status == status)

    # Grouping by user

    query = query.group_by(Task.assignee_user_id)

    # print(query)

    task_list_by_period = query.all()

    # Front end expects it in this way
    labels, values = zip(*task_list_by_period)

    return labels, values
# return query.count()