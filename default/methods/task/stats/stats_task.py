from methods.regular.regular_api import *
from shared.database.task.task import Task

from sqlalchemy import func

import datetime


@routes.route('/api/v1/project/<string:project_string_id>/stats/task',
              methods = ['POST'])
@limiter.limit("20 per day")
def stats_task_api(project_string_id):
    spec_list = [{'date_from': str},
                 {'date_to': str},
                 {'status': str},
                 {'job_id': {
                     "required": False,
                     "type": int,
                 }},
                 {'mode': str}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        user = User.get(session)
        if input.get('job_id'):
            project = Project.get_by_string_id(session, project_string_id = project_string_id)
            stats = stats_task_core(session = session,
                                    project = project,
                                    date_from = input['date_from'],
                                    date_to = input['date_to'],
                                    status = input['status'],
                                    job_id = input['job_id'])
        else:
            stats = stats_task_core_project(session = session,
                                            project_string_id = project_string_id,
                                            date_from = input['date_from'],
                                            date_to = input['date_to'],
                                            status = input['status'])

        log['success'] = True
        return jsonify(log = log,
                       stats = stats), 200


@Job_permissions.by_job_id(
    project_role_list = ["admin", "Editor", "Viewer"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
def stats_task_core(session,
                    project,
                    date_from,
                    date_to,
                    status,
                    job_id):
    # if using time created
    query = session.query(func.date_trunc('day', Task.time_created),
                          func.count(Task.id))

    date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d")
    date_to = datetime.datetime.strptime(date_to, "%Y-%m-%d")

    # Set to next day so we can use default of 00:00 start
    # instead of midnight. Otherwise results during the
    # day get excluded
    date_to += datetime.timedelta(days = 1)

    query = query.filter(Task.time_created >= date_from)
    query = query.filter(Task.time_created < date_to)
    query = query.filter(Task.project_id == project.id)

    if status:
        if status != "all":
            query = query.filter(Task.status == status)

    if job_id:
        query = query.filter(Task.job_id == job_id)

    # Grouping by day

    query = query.group_by(func.date_trunc('day', Task.time_created))

    query = query.order_by(func.date_trunc('day', Task.time_created))

    # print(query)

    task_list_by_period = query.all()

    # TODO handle task_list_by_day being None
    dates_list = [x[0] for x in task_list_by_period]
    with_missing_dates = Stats.fill_missing_dates(date_from = date_from,
                                                  date_to = date_to,
                                              known_dates_list = dates_list)
    labels = []
    values = []
    for date in with_missing_dates:
        labels.append(date)
        if date in dates_list:
            index = dates_list.index(date)
            values.append(task_list_by_period[index][1])
        else:
            values.append(0)

    count_task = sum(values)

    return {'labels': labels,
            'values': values,
            'count_task': count_task}


@Project_permissions.user_has_project(Roles = ["admin", "Editor", "annotator", "viewer"],
                                      apis_user_list = ["api_enabled_builder"])
def stats_task_core_project(session,
                            project_string_id,
                            date_from,
                            date_to,
                            status):
    # if using time created
    project = Project.get_by_string_id(session, project_string_id = project_string_id)
    query = session.query(func.date_trunc('day', Task.time_created),
                          func.count(Task.id))

    date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d")
    date_to = datetime.datetime.strptime(date_to, "%Y-%m-%d")

    # Set to next day so we can use default of 00:00 start
    # instead of midnight. Otherwise results during the
    # day get excluded
    date_to += datetime.timedelta(days = 1)

    query = query.filter(Task.time_created >= date_from)
    query = query.filter(Task.time_created < date_to)
    query = query.filter(Task.project_id == project.id)

    if status:
        if status != "all":
            query = query.filter(Task.status == status)

    # Grouping by day

    query = query.group_by(func.date_trunc('day', Task.time_created))

    query = query.order_by(func.date_trunc('day', Task.time_created))

    # print(query)

    task_list_by_period = query.all()

    dates_list = [x[0] for x in task_list_by_period]
    # TODO handle task_list_by_day being None

    with_missing_dates = Stats.fill_missing_dates(date_from = date_from,
                                                  date_to = date_to,
                                                  known_dates_list = dates_list)

    labels = []
    values = []
    for date in with_missing_dates:
        labels.append(date)
        if date in dates_list:
            index = dates_list.index(date)
            values.append(task_list_by_period[index][1])
        else:
            values.append(0)

    count_task = sum(values)

    return {'labels': labels,
            'values': values,
            'count_task': count_task}
