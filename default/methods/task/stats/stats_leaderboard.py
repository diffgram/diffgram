from methods.regular.regular_api import *
from shared.database.task.task import Task
from sqlalchemy import func, inspect
from flask_caching import Cache

cache = Cache()

@routes.route('/api/v1/diffgram/stats/leaderboard',
              methods=['POST'])
@General_permissions.grant_permission_for(Roles=[])  # Super admin allowed by default
@limiter.limit("20 per day")
@cache.cached(timeout=3600)  # Cache for 1 hour
def stats_leaderboard_api():
    """
    Get the leaderboard stats for a given date range and status.

    Input parameters:
    - date_from (str): The start date of the range in the format 'YYYY-MM-DD'.
    - date_to (str): The end date of the range in the format 'YYYY-MM-DD'.
    - status (str): The task status to filter by. Default is 'completed'.

    Returns:
    - log (dict): A dictionary containing the log information.
    - labels (list): A list of user IDs.
    - values (list): A list of task counts for each user.
    """
    spec_list = [{'date_from': str}, {'date_to': str}, {'status': str}]

    log, input, untrusted_input = regular_input.master(request=request, spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    if 'date_to' not in input:
        input['date_to'] = datetime.date.today().strftime('%Y-%m-%d')

    with sessionMaker.session_scope() as session:
        labels, values = stats_leaderboard_core(session=session,
                                                date_from=input['date_from'],
                                                date_to=input['date_to'],
                                                status=input.get('status', 'completed'))

        log['success'] = True
        return jsonify(log=log, labels=labels, values=values), 200


@cache.cached(timeout=3600)  # Cache for 1 hour
def stats_leaderboard_core(session, date_from, date_to, status='completed'):
    query = session.query(Task.assignee_user_id, func.count(Task.id)).filter(
        Task.time_created >= date_from,
        Task.time_created <= date_to,
        Task.status == status
    ).group_by(Task.assignee_user_id)

    # Limit the number of results to prevent performance issues
    query = query.limit(100)

    task_list_by_period = query.all()

    # Front end expects it in this way
    labels, values = zip(*task_list_by_period)

    return labels, values
