from methods.regular.regular_api import *
from shared.database.task.job.job import Job


@routes.route('/api/v1/diffgram/stats/job',
              methods = ['POST'])
@General_permissions.grant_permission_for(Roles = [])  # Super admin allowed by default
@limiter.limit("20 per day")
def stats_job_api():
    spec_list = [{'date_from': str},
                 {'date_to': str},
                 {'status': str}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        count = stats_job_core(session = session,
                               date_from = input['date_from'],
                               date_to = input['date_to'])

        log['success'] = True
        return jsonify(log = log,
                       count = count), 200


def stats_job_core(session,
                   date_from,
                   date_to):
    # date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d")
    # date_to = datetime.datetime.strptime(date_to, "%Y-%m-%d")

    # if using time created

    query = session.query(Job).filter(Job.time_created > date_from)

    return query.count()

