# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.user import User
from shared.database.project import Project
from shared.database.task.job.job_launch import JobLaunch


@routes.route('/api/v1' +
              '/job-launch/list',
              methods=['POST'])
@General_permissions.grant_permission_for(
    Roles=['normal_user'],
    apis_user_list=["builder_or_trainer"])
def job_launch_list_api():
    # Would prefer to check all the inputs directly
    # But then would have to revist whole metadata proposed concept
    # for search
    # TODO roll this into concept of reviewing regular method's
    # default values, ie allowing values but not requiring them

    spec_list = [{"metadata": dict}]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        Job_list, metadata = job_launch_list_core(session=session, metadata_proposed=input['metadata'])
        if 'error' in log and len(log['error'].keys()) >= 1:
            return jsonify(log), 400
        log['success'] = True
        return jsonify(job_launch_list=Job_list,
                       metadata=metadata,
                       log=log), 200


def default_metadata(meta_proposed):
    meta = {}

    meta['limit'] = 50

    meta["start_index"] = 0

    meta["job_ids"] = meta_proposed.get("job_ids", None)
    meta["status"] = meta_proposed.get("status", None)
    meta["date_from"] = meta_proposed.get("date_from", None)
    meta["date_to"] = meta_proposed.get("date_to", None)
    meta["builder_or_trainer"] = meta_proposed.get("builder_or_trainer", None)
    meta["time_created"] = meta_proposed.get("time_created", None)
    meta["time_completed"] = meta_proposed.get("time_completed", None)

    meta["project_string_id"] = meta_proposed.get("project_string_id", None)

    meta["org"] = meta_proposed.get("org", "None")

    return meta


def job_launch_list_core(session,
                         metadata_proposed,
                         output_mode="serialize"):
    """
        Get the job_launch objects based on filters in
        metadata_proposed.

    """

    meta = default_metadata(metadata_proposed)
    output_job_launch_list = []
    limit_counter = 0

    # CAUTION
    # Multiple "modes", for output and trainer builder, maybe more in future
    builder_or_trainer_mode = meta['builder_or_trainer']['mode']

    # It doesn't really make sense to have this here
    # Should be part of some other meta data checking or something.
    if builder_or_trainer_mode not in ["builder", "trainer"]:
        raise Forbidden("Invalid builder_or_trainer_mode mode.")

    query = session.query(JobLaunch).join(Job)

    user = User.get(session)

    if user.last_builder_or_trainer_mode != builder_or_trainer_mode:
        raise Forbidden("Invalid user relation to builder_or_trainer_mode mode.")

    ### START FILTERS ###

    if meta["status"]:
        if meta["status"] != "All":
            query = query.filter(JobLaunch.status == meta["status"])
    if meta["date_from"]:
        date_from = datetime.datetime.strptime(meta["date_from"], "%Y-%m-%d")
        date_from = date_from.replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(JobLaunch.time_created >= date_from)
    if meta["date_to"]:
        date_to = datetime.datetime.strptime(meta["date_to"], "%Y-%m-%d")
        date_to = date_to.replace(hour=0, minute=0, second=0, microsecond=0)

        query = query.filter(JobLaunch.time_created <= date_to)

    if meta["job_ids"]:
        query = query.filter(Job.id.in_(meta["job_ids"]))

    # Also assumes org is None.
    # Actually this should be complimentary still
    if meta["project_string_id"]:
        project = Project.get_by_string_id(session=session, project_string_id=meta["project_string_id"])
        query = query.filter(Job.project_id == project.id)
    #### END FILTERS ###

    query = query.order_by(Job.time_created.desc())
    query = query.limit(meta["limit"])
    query = query.offset(meta["start_index"])

    job_launch_list = query.all()

    if output_mode == "serialize":

        for job_launch in job_launch_list:
            serialized = job_launch.serialize_for_list_view(session=session)

            output_job_launch_list.append(serialized)
            limit_counter += 1

    meta['end_index'] = meta['start_index'] + len(output_job_launch_list)
    meta['length_current_page'] = len(output_job_launch_list)

    if limit_counter == 0:
        meta['no_results_match_meta'] = True

    return output_job_launch_list, meta
