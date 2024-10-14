from methods.regular.regular_api import *  # Import regular API methods
from shared.database.task.job.job import Job  # Import Job class from the job module


@routes.route('/api/v1/diffgram/stats/job', methods=['POST'])  # Define the API endpoint for job statistics
@General_permissions.grant_permission_for(Roles=[])  # Super admin allowed by default
@limiter.limit("20 per day")  # Limit 20 requests per day
def stats_job_api():
    spec_list = [{'date_from': str},  # Define the input schema for the API
                 {'date_to': str},
                 {'status': str}]

    log, input, untrusted_input = regular_input.master(request=request,  # Validate and parse the input
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400  # Return an error if input validation fails

    with sessionMaker.session_scope() as session:  # Start a database session
        count = stats_job_core(session=session,  # Call the stats_job_core function
                               date_from=input['date_from'],
                               date_to=input['date_to'])

        log['success'] = True  # Set success flag to True
        return jsonify(log=log,  # Return the log object
                       count=count), 200  # Return the count of jobs


def stats_job_core(session,  # The database session object
                   date_from,  # The start date for the job statistics
                   date_to):  # The end date for the job statistics
    # date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d")  # Convert the date strings to datetime objects
    # date_to = datetime.datetime.strptime(date_to, "%Y-%m-%d")

    # if using time created

    query = session.query(Job).filter(Job.time_created > date_from)  # Query for jobs created after the start date

    return query.count()  # Return the count of jobs

