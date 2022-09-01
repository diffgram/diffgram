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

from shared.database.tag.tag import Tag
from shared.database.tag.tag import JobTag


@routes.route('/api/v1/job/list',
              methods = ['POST'])
def job_list_api():
    spec_list = [{"metadata": dict}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        Job_list, metadata = job_view_core(session = session,
                                           metadata_proposed = input['metadata'])

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

    meta = default_metadata(metadata_proposed)

    output_file_list = []
    limit_counter = 0

    builder_or_trainer_mode = "builder"

    query = session.query(Job)

    ## Until refactor to support "market" better, default to project
    ## This included the permissions
    query = filter_by_project(session = session,
                              project_string_id = meta["project_string_id"],
                              query = query)

    user = User.get(session)

    if user:
        if user.last_builder_or_trainer_mode != builder_or_trainer_mode:
            raise Forbidden("Invalid user relation to builder_or_trainer_mode mode.")
    job_type = None

    if meta["type"]:
        if meta["type"] != "All":
            job_type = meta["type"]

    if job_type:
        query = query.filter(Job.type == job_type)

    if meta.get('members'):
        members = session.query(Member).filter(Member.id.in_(meta.get('members')))
        user_ids = [m.user_id for m in members]
        rels = session.query(User_To_Job).filter(User_To_Job.user_id.in_(user_ids))
        job_ids = [rel.job_id for rel in rels]
        query = query.filter(Job.id.in_(job_ids))

    project = Project.get(session, meta["project_string_id"])

    query = add_tag_filters(query, meta, session, project)

    if meta["my_jobs_only"]:

        if builder_or_trainer_mode == "builder":
            query = query.filter(Job.member_created == user.member)

        if builder_or_trainer_mode == "trainer":
            attached_query = session.query(User_To_Job).filter(
                User_To_Job.user_id == user.id).subquery('sub_query')

            query = query.filter(Job.id == attached_query.c.job_id)

    else:
        if builder_or_trainer_mode == "trainer" and job_type == "Exam":
            query = query.filter(Job.is_template == True)

    if meta["instance_type"]:
        if meta["instance_type"] != "All":
            query = query.filter(Job.instance_type == meta["instance_type"])

    if meta["job_ids"]:
        query = query.filter(Job.id.in_(meta["job_ids"]))

    if meta["parent_id"]:
        query = query.filter(Job.parent_id == meta["parent_id"])

    if builder_or_trainer_mode == "builder":

        # Status can be seperate from project...
        if meta["status"]:
            if meta["status"] != "All":
                if not isinstance(meta["status"], list):
                    meta["status"] = [meta["status"]]
                query = query.filter(Job.status.in_(meta["status"]))

        if meta["share_type"] == "Market":
            query = query.filter(Job.status.in_(("active", "complete")))

    if builder_or_trainer_mode == "trainer":
        query = query.filter(Job.status.in_(("active", "complete")))

    query = add_name_search_filter(query, meta)

    query = query.order_by(Job.time_created.desc())

    if meta.get("limit") is not None:
        query = query.limit(meta["limit"])

    query = query.offset(meta["start_index"])

    # Avoid multiple queries on serializer by fetching joined data
    query = query.options(joinedload(Job.completion_directory))
    query = query.options(joinedload(Job.label_schema))

    job_list = query.all()

    if output_mode == "serialize":

        for job in job_list:

            if meta["data_mode"] == "name_and_id_only":
                serialized = job.serialize_minimal_info()
            elif meta["data_mode"] == "with_tags":
                serialized = job.serialize_with_tags(session = session)
            else:
                serialized = job.serialize_for_list_view(session = session)

            output_file_list.append(serialized)
            limit_counter += 1

    meta['end_index'] = meta['start_index'] + len(job_list)
    meta['length_current_page'] = len(output_file_list)

    if limit_counter == 0:
        meta['no_results_match_meta'] = True

    return output_file_list, meta


def add_tag_filters(query, meta, session, project):
    if meta["tag_list"]:
        tag_id_list = []
        for tag in meta["tag_list"]:
            if isinstance(tag, int):
                tag_id_list.append(tag)
        jobtag_list = JobTag.get_many(
            session = session,
            tag_id_list = tag_id_list,
            project_id = project.id)
        job_ids = [jobtag.job_id for jobtag in jobtag_list]
        query = query.filter(Job.id.in_(job_ids))

    return query


def add_name_search_filter(query, meta):
    if meta["search"] is not None:
        search_text = f"%{meta['search']}%"
        query = query.filter(Job.name.ilike(search_text))

    return query


def default_metadata(meta_proposed):
    server_side_limit = 100  # Clarify this is limit of results returned PER PAGE , user can go to next page to see more results

    # status?

    meta = {}

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

    meta["tag_list"] = meta_proposed.get("tag_list", None)

    meta["org"] = meta_proposed.get("org", "None")

    meta["share_type"] = meta_proposed.get("share_type", None)

    if meta["share_type"] not in ["market", "project", "org"]:
        meta["share_type"] = "project"

    meta["limit"] = meta_proposed.get('limit', 50)

    return meta


@Project_permissions.user_has_project(["admin", "Editor", "Viewer"])
def filter_by_project(session,
                      project_string_id,
                      query):
    project = Project.get(session = session,
                          project_string_id = project_string_id)

    query = query.filter(Job.project == project)
    return query
