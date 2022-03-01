# OPENCORE - ADD
from methods.regular.regular_api import *

from shared.database.user import User
from shared.database.project import Project

from shared.database.source_control.working_dir import WorkingDir

from shared.database.task.job.job import Job
from shared.database.auth.member import Member
from shared.database.task.job.user_to_job import User_To_Job
from sqlalchemy import or_
from sqlalchemy.orm import joinedload


@routes.route('/api/v1/job/list',
              methods = ['POST'])
@General_permissions.grant_permission_for(
    Roles = ['normal_user'],
    apis_user_list = ["builder_or_trainer"])
def job_list_api():
    # Would prefer to check all the inputs directly
    # But then would have to revist whole metadata proposed concept
    # for search
    # TODO roll this into concept of reviewing regular method's
    # default values, ie allowing values but not requiring them

    spec_list = [{"metadata": dict}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        ### MAIN ###
        Job_list, metadata = job_view_core(session = session,
                                           metadata_proposed = input['metadata'])
        ############
        log['success'] = True
        return jsonify(Job_list = Job_list,
                       metadata = metadata,
                       log = log), 200


def job_view_core(session,
                  metadata_proposed,
                  output_mode = "serialize",
                  user = None):
    """
    output_mode
        serialize is in context of web, ie serialize the resulting list
            currently defaults to this context
        objects returns the database objects, ie for auto commit

    """

    # CAUTION some of these settings get overriden / effected by
    # default_metadata below!!!
    meta = default_metadata(metadata_proposed)

    start_time = time.time()
    output_file_list = []
    limit_counter = 0

    # CAUTION
    # Multiple "modes", for output and trainer builder, maybe more in future
    builder_or_trainer_mode = meta['builder_or_trainer']['mode']

    # It doesn't really make sense to have this here
    # Should be part of some other meta data checking or something.
    if builder_or_trainer_mode not in ["builder", "trainer"]:
        raise Forbidden("Invalid builder_or_trainer_mode mode.")

    query = session.query(Job)

    # TODO may want to make this a flag, ie in case
    # super admin wants to see it.
    query = query.filter(Job.hidden == False)

    # Caution there's "Status" check query things buried at the bottom
    # here

    # May also want to view jobs by multiple users!!!

    user = User.get(session)

    if user.last_builder_or_trainer_mode != builder_or_trainer_mode:
        raise Forbidden("Invalid user relation to builder_or_trainer_mode mode.")

    ### START FILTERS ###

    job_type = None
    if meta["type"]:
        if meta["type"] != "All":
            job_type = meta["type"]

    if builder_or_trainer_mode == "trainer":
        pass

    if job_type:
        query = query.filter(Job.type == job_type)
    if meta.get('members'):
        members = session.query(Member).filter(Member.id.in_(meta.get('members')))
        user_ids = [m.user_id for m in members]
        rels = session.query(User_To_Job).filter(User_To_Job.user_id.in_(user_ids))
        job_ids = [rel.job_id for rel in rels]
        query = query.filter(Job.id.in_(job_ids))

    if meta["my_jobs_only"]:

        if builder_or_trainer_mode == "builder":
            query = query.filter(Job.member_created == user.member)

        if builder_or_trainer_mode == "trainer":
            attached_query = session.query(User_To_Job).filter(
                User_To_Job.user_id == user.id).subquery('sub_query')

            query = query.filter(Job.id == attached_query.c.job_id)

        """
        # Prior combo method for both builder and trainer
        query = query.filter(or_(Job.member_created == user.member,
                                Job.id == attached_query.c.job_id))
        """

    else:

        # Trainers should be able to see their instance of an exam
        # And the templates of other exams?

        # TODO not clear how this should effect builders

        if builder_or_trainer_mode == "trainer" and job_type == "Exam":
            query = query.filter(Job.is_template == True)

    # Disable field, till fully supported.
    """
    if meta["field"]:
        if meta["field"] != "All":

            field = Field.get_by_name(session = session,
                                      name = meta["field"])

            if field:
                query = query.filter(Job.field == field)
    """
    # TODO could we combine these methods seems like repetition

    if meta["instance_type"]:
        if meta["instance_type"] != "All":
            query = query.filter(Job.instance_type == meta["instance_type"])

    if meta["job_ids"]:
        query = query.filter(Job.id.in_(meta["job_ids"]))

    if meta["parent_id"]:
        query = query.filter(Job.parent_id == meta["parent_id"])

    if builder_or_trainer_mode == "builder":

        # Permissions in wrapper on this function
        # Note: the function filter_by_project() is taking almost 1s (most of this thanks to permissions)
        if meta["share_type"] == "project":
            query = filter_by_project(session = session,
                                      project_string_id = meta["project_string_id"],
                                      query = query)

        # Status can be seperate from project...
        if meta["status"]:
            if meta["status"] != "All":
                if not isinstance(meta["status"], list):
                    meta["status"] = [meta["status"]]
                query = query.filter(Job.status.in_(meta["status"]))

        # Also assumes org is None.
        # Actually this should be complimentary still
        if meta["share_type"] == "Market":
            query = query.filter(Job.status.in_(("active", "complete")))

    if builder_or_trainer_mode == "trainer":
        query = query.filter(Job.status.in_(("active", "complete")))

    # The by API thing is not yet supported and this is confusing things
    # For user level search
    # if meta["org"] == "None":
    # Restrict trainers to market only jobs. (if no org is present)
    # A user that wants to share the job with project should be a builder...

    # TODO review this, confusing / if shared with org...
    # One part of the issue is need better checking on what's an allowed shared type...

    # CAUTION market is caps senstive
    #	query = query.filter(Job.share_type == "market")

    # If mode is trainer then force to use org id

    if meta["search"] is not None:
        search_text = f"%{meta['search']}%"
        query = query.filter(Job.name.ilike(search_text))

    query = query.order_by(Job.time_created.desc())

    #### END FILTERS ###

    query = query.limit(meta["limit"])
    query = query.offset(meta["start_index"])

    # Avoid multiple queries on serializer by fetching joined data
    query = query.options(joinedload(Job.completion_directory))

    job_list = query.all()

    if output_mode == "serialize":

        for job in job_list:

            # optional place can re run this
            # more for edge cases
            # job.update_file_count_statistic(session)

            if meta["data_mode"] == "name_and_id_only":
                serialized = job.serialize_minimal_info()
            else:
                serialized = job.serialize_for_list_view(session = session)

            output_file_list.append(serialized)
            limit_counter += 1

    timer = time.time()

    meta['end_index'] = meta['start_index'] + len(job_list)
    meta['length_current_page'] = len(output_file_list)

    if limit_counter == 0:
        meta['no_results_match_meta'] = True

    end_time = time.time()

    return output_file_list, meta


def default_metadata(meta_proposed):
    server_side_limit = 100  # Clarify this is limit of results returned PER PAGE , user can go to next page to see more results

    # status?

    meta = {}

    meta['limit'] = 50

    meta["start_index"] = 0

    meta["my_jobs_only"] = meta_proposed.get("my_jobs_only", None)
    meta["search"] = meta_proposed.get("search", None)
    meta["members"] = meta_proposed.get("members", None)
    meta["job_ids"] = meta_proposed.get("job_ids", None)
    meta["builder_or_trainer"] = meta_proposed.get("builder_or_trainer", None)
    meta["field"] = meta_proposed.get("field", None)
    meta["category"] = meta_proposed.get("category", None)
    meta["type"] = meta_proposed.get("type", None)
    meta["instance_type"] = meta_proposed.get("instance_type", None)
    meta["status"] = meta_proposed.get("status", None)
    meta["parent_id"] = meta_proposed.get("parent_id", None)

    meta["data_mode"] = meta_proposed.get("data_mode", None)
    meta["project_string_id"] = meta_proposed.get("project_string_id", None)

    # SPECIAL for now, condition on string None instead of actual None
    # Since we are naively sending string None from front end if an org exists
    # BUT if there aren't any orgs we want to run the search like normal...
    # TODO review this

    meta["org"] = meta_proposed.get("org", "None")

    meta["share_type"] = meta_proposed.get("share_type", None)

    # Temp check here...
    if meta["share_type"] not in ["market", "project", "org"]:
        # TODO prefer returning an error I think
        meta["share_type"] = "project"

    """
    # WIP WIP WIP

    #meta['name'] = meta_proposed.get("name", None)
    #meta['search_term'] = meta_proposed.get('search_term', None)
    meta_limit_proposed = meta_proposed.get('limit', None)
        
    if meta_limit_proposed:
        if meta_limit_proposed <= server_side_limit:
            meta["limit"] = meta_limit_proposed
        else:
            meta["limit"] = server_side_limit
                    
    request_next_page = meta_proposed.get('request_next_page', None)

    if request_next_page is True and meta_proposed.get('previous', None):
        meta['image']["start_index"] = int(meta_proposed['previous']['image'].get('end_index', 0))
    """

    return meta


@Project_permissions.user_has_project(["admin", "Editor", "Viewer"])
def filter_by_project(session,
                      project_string_id,
                      query):
    project = Project.get(session = session,
                          project_string_id = project_string_id)

    query = query.filter(Job.project == project)
    return query
