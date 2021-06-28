try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

from shared.database.user import UserbaseProject
from shared.database.task.job.job import Job
from shared.database.source_control.file_diff import file_difference_and_serialize_for_web
from sqlalchemy import asc
from sqlalchemy import desc
from shared.query_engine.query_creator import QueryCreator
from shared.query_engine.sqlalchemy_query_exectutor import SqlAlchemyQueryExecutor


@routes.route('/api/v1/file/view',
              methods = ['POST'])
def view_file_by_id():  # Assumes permissions handled later with Project_permissions
    """

    Some key differences vs other routes

    * Does not assume linked to project
    * Does not assume user (could be api auth)

    So anyone with the link is the hash
    Public is something else

    Permissions
        a) Auth by including project
        b) Auth by some extra "link" or code (could follow similar
            structure for "share by " links

    with_labels is a future id if we do auth without project

    In context of video mode, including all instances
        in single go no longer makes sense

    The main difference from "task" is that it uses the project permissions
    and it's "just" for a single file, which does not have to relate to a
    task.
        Relevant for admins, and in future could be relevant for say
        inference results, or input verification / jumping to, etc.

    """
    spec_list = [{'file_id': int},
                 {'project_string_id': str}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with_labels = False
    label_dict = {}
    file_serialized = None

    with sessionMaker.session_scope() as session:

        Project_permissions.by_project_core(
            project_string_id = input['project_string_id'],
            Roles = ["admin", "Editor", "Viewer", "allow_if_project_is_public"])

        project = Project.get(
            session = session,
            project_string_id = input['project_string_id'])

        file = File.get_by_id_and_project(
            session = session,
            project_id = project.id,
            file_id = input['file_id'],
            directory_id = project.directory_default_id  # fallback only
        )

        if file:
            if with_labels is True:
                # For "existing" labels attached to instance
                label_dict = file.serialize_all_labels_in_attached_instance_list(
                    session = session)

            file_serialized = file.serialize_with_type(session)
            log['success'] = True
        else:
            log['error']['no file'] = "File not found. Are you in the right project?"
            return jsonify(log = log), 403

        return jsonify(log = log,
                       label_dict = label_dict,
                       file = file_serialized)


@routes.route('/api/project/<string:project_string_id>/file/<int:file_id>/diff/previous',
              methods = ['GET'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer"])
def view_file_diff(project_string_id, file_id):
    """


    """
    with sessionMaker.session_scope() as session:
        # project = Project.get(session, project_string_id)
        # user_requested = session.query(User).filter(User.username == username).one()

        result, instance_list = file_difference_and_serialize_for_web(
            session,
            file_id)
        if result is True:
            out = jsonify(success = True,
                          instance_list = instance_list
                          )
            return out, 200, {'ContentType': 'application/json'}
        else:
            out = jsonify(success = False)
            return out, 200, {'ContentType': 'application/json'}


## Allow post for now here
#   See annotation_core get_instances() it defaults to a post
# instance_list
@routes.route('/api/v1/task/<int:task_id>/annotation/list',
              methods = ['GET', 'POST'])
@Permission_Task.by_task_id(apis_user_list = ["builder_or_trainer"])
def task_get_annotation_list_api(task_id):
    with sessionMaker.session_scope() as session:
        task = Task.get_by_id(session = session,
                              task_id = task_id)

        # TODO Review the function get_annotations_common()
        # which assummes we need to check file permissions still,
        # ie (via project) where as here we don't...

        file_serialized = task.file.serialize_with_annotations(session = session)

        return jsonify(success = True,
                       file_serialized = file_serialized), 200

    # instance_list


@routes.route('/api/project/<string:project_string_id>/' +
              'file/<string:file_id>/annotation/list',
              methods = ['POST'])
@Project_permissions.user_has_project(
    ["admin", "Editor", "Viewer", "allow_if_project_is_public"])
def instance_list(project_string_id, file_id):
    spec_list = [
        {'job_id': None}
    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        return get_annotations_common(
            session,
            project_string_id,
            file_id
        )


def get_annotations_common(
    session,
    project_string_id,
    file_id,
    directory_id = None
):
    """
    this assumes that it's for an image
    not a video...

    """

    if file_id is None or file_id == "undefined":
        return jsonify("No file_id"), 400

    message = ""

    # a task does not store in project default directory,
    # so this check will fail for tasks,
    # usetask_get_annotation_list_api() instead"
    file = File.get_by_id_and_project(
        session = session,
        project_id = Project.get(session, project_string_id).id,
        file_id = file_id)

    if file:
        file_serialized = file.serialize_with_annotations(session)
    else:
        message += " File not in valid project directory."

        return jsonify(
            success = False,
            message = message
        ), 400

    return jsonify(success = True,
                   file_serialized = file_serialized), 200


# video buffer /buffer/start

# From Task route
@routes.route('/api/v1/task/<int:task_id>' +
              '/video/file_from_task/instance/buffer' +
              '/start/<int:start>' +
              '/end/<int:end>/list',
              methods = ['POST'])
@Permission_Task.by_task_id(apis_user_list = ["builder_or_trainer"])
def get_instance_buffer_web_from_task(task_id, start, end):
    with sessionMaker.session_scope() as session:
        task = Task.get_by_id(
            session = session,
            task_id = task_id)

        return get_instance_buffer_master(
            session, task.file, start, end)


@routes.route('/api/project/<string:project_string_id>' +
              '/video/<int:video_file_id>/instance/buffer' +
              '/start/<int:start>' +
              '/end/<int:end>/list',
              methods = ['POST'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer", "allow_if_project_is_public"])
def get_instance_buffer_web(project_string_id, video_file_id, start, end):
    with sessionMaker.session_scope() as session:
        """
        The directory is still here because we could have had old files
        that were in a *non* defualt directory... so still do this for now
            otherwise was hoping could just move to project.directory_default_id
            as the fallback.
        """

        data = request.get_json(force = True)
        directory_id = data.get('directory_id', None)
        project = Project.get(session, project_string_id)

        directory = WorkingDir.get_with_fallback(
            session = session,
            project = project,
            directory_id = directory_id)

        if directory is False:
            return jsonify("Invalid directory"), 400

        video_file = File.get_by_id_and_project(
            session = session,
            project_id = project.id,
            file_id = video_file_id,
            directory_id = directory.id)  # Fallback

        return get_instance_buffer_master(
            session, video_file, start, end)


def get_instance_buffer_master(session, video_file, start, end):
    if video_file is None:
        return jsonify(success = True), 400

    instance_buffer_dict = get_instance_buffer(
        session,
        video_file.id,
        start,
        end)

    return jsonify(success = True,
                   instance_buffer_dict = instance_buffer_dict
                   ), 200


def get_instance_buffer(session, video_file_id, start, end):
    """
    Motivation is that this function could get called quite often
    and caching is questionable given how much we expect it to change.

    Testing, if say start is frame 587 we expect this
    to return the instances for frame 587 in the 0th index.
    And then, as many further instances up to the end.

    A trick here is that it uses the "count instances changed"

    I also wonder if we could "build" this in the background more
    proactively

    Re Limit
        If there are no files for longer videos we like to return longer
        segments to reduce loading.

    """

    # limit
    if end - start >= 1000:
        end = start + 1000

    # Allow buffer to go back, ie go back 1 frame works.
    # Careful max here since otherwise it gets it for full video

    start = max(0, start - 10)

    image_file_list = WorkingDirFileLink.image_file_list_from_video(
        session = session,
        video_parent_file_id = video_file_id,
        start = start,
        end = end,
        has_count_instances_changed = True
    )

    buffer = {}

    # Careful, we need to start from the start number here
    # (since it may not be 0)

    # We always return the constructed array here
    # Because when we play/pause, if it was indeed empty we don't want
    # to have to go back for it.

    # We could also return a buffer on either side...
    # Just cap at 0
    # (That way can go back and forth more easily

    """
    Cache addition
        Main concern is that if we change anything in terms of instance 
        structure we will have to invalidate the data
        ie by calling file.clear_cache()
        or file.set_cache_key_dirty('instance_list')

        Right now this only checks it exists,
        We assume that annotation.py is responsible to update instances as they
        change / are edited.
    """

    for i in range(start, end):
        buffer[i] = []

    for file in image_file_list:
        file.set_cache_key_dirty('instance_list')
        buffer[file.frame_number] = file.get_with_cache(
            cache_key = 'instance_list',
            cache_miss_function = file.serialize_instance_list_only,
            session = session)

    # TODO not quite sure how we want to store / pass this
    # In context this is stored on multiple files
    # cache_info = file.cache_dict.get('__info') if file.get('cache_dict') else None

    return buffer


@routes.route('/api/project/<string:project_string_id>' +
              '/user/<string:username>/file/list',
              methods = ['POST'])
@Project_permissions.user_has_project([
    "admin", "Editor", "Viewer", "allow_if_project_is_public"])
def view_file_list_web_route(project_string_id, username):
    """
        The “user” sub concept is deprecated
    """

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        data = request.get_json(force = True)
        metadata_proposed = data.get('metadata')

        if not metadata_proposed:
            return jsonify("Error no metadata"), 400

        directory = WorkingDir.get_with_fallback(
            session = session,
            directory_id = metadata_proposed.get("directory_id", None),
            project = project)

        if directory is False:
            return jsonify("Error with directory"), 400

        user = User.get(session)
        if user:
            member = user.member
        else:
            client_id = request.authorization.get('username', None)
            auth = Auth_api.get(session, client_id)
            member = auth.member

        file_browser_instance = File_Browser(
            session = session,
            project = project,
            directory = directory,
            metadata_proposed = metadata_proposed,
            member = member
        )

        output_file_list = file_browser_instance.file_view_core(
            mode = "serialize")

        return jsonify(file_list = output_file_list,
                       metadata = file_browser_instance.metadata), 200


class File_Browser():
    """

    """

    def __init__(
        self,
        session,
        project,
        directory,
        metadata_proposed,
        member
    ):

        self.session = session
        self.project = project
        self.directory = directory
        self.member = member

        self.metadata_proposed = metadata_proposed
        self.default_metadata()

    def default_metadata(self):

        if self.metadata_proposed is None:
            self.metadata_proposed = {}

        server_side_limit = 1000  # Clarify this is limit of results returned PER PAGE , user can go to next page to see more results
        annotation_status_settings = None
        machine_made_setting = None
        filter_media_type = None
        search_term = None
        instructions = None

        self.metadata = {}

        self.metadata['job_id'] = self.metadata_proposed.get("job_id", None)
        self.metadata['issues_filter'] = self.metadata_proposed.get("issues_filter", None)

        self.metadata['file'] = {}
        self.metadata['query'] =  self.metadata_proposed.get("query", None)
        self.metadata['limit'] = 25

        self.metadata['directory_id'] = self.metadata_proposed.get("directory_id", None)
        self.metadata['date_from'] = self.metadata_proposed.get("date_from", None)
        self.metadata['date_to'] = self.metadata_proposed.get("date_to", None)

        # Now that we have combined file and video
        # this is primary index (label is secondary)
        # And front end just hates empty layed dicts so doing this for now
        self.metadata["start_index"] = 0

        self.metadata['label'] = {}
        self.metadata['label']["start_index"] = 0

        self.metadata['file_view_mode'] = self.metadata_proposed.get("file_view_mode", None)

        self.metadata['search_term'] = self.metadata_proposed.get('search_term', None)
        self.metadata['machine_made_setting'] = self.metadata_proposed.get('annotations_are_machine_made_setting', None)
        self.metadata['annotation_status'] = self.metadata_proposed.get('annotation_status', None)

        metadata_limit_proposed = self.metadata_proposed.get('limit', None)

        self.metadata['media_type'] = self.metadata_proposed.get('media_type', None)

        self.metadata['job_id'] = self.metadata_proposed.get('job_id', None)

        if metadata_limit_proposed:
            if metadata_limit_proposed <= server_side_limit:
                self.metadata["limit"] = metadata_limit_proposed
            else:
                self.metadata["limit"] = server_side_limit

        request_next_page = self.metadata_proposed.get('request_next_page', None)

        # TODO this makes a lot of assumptions about which fires first,
        # ie would rather have a "request_next_page_kind" or something...

        # Why need meta data previous here?
        # mainly based off 'end_index'
        if request_next_page is True and self.metadata_proposed.get('previous', None):
            self.metadata["start_index"] = int(
                self.metadata_proposed['previous'].get('end_index', 0))

        # self.metadata['label']["start_index"] = int(self.metadata_proposed['previous']['label'].get('end_index', 0))

        request_previous_page = self.metadata_proposed.get('request_previous_page', None)
        if request_previous_page is True:
            # this seems kinda hacky to use the limit...
            if self.metadata_proposed['previous'].get('start_index'):
                self.metadata["start_index"] = int(
                    self.metadata_proposed['previous'].get('start_index')) - int(self.metadata["limit"])
            if self.metadata["start_index"] < 0:
                self.metadata["start_index"] = 0

        self.metadata['pagination'] = self.metadata_proposed.get('pagination', {})

    def build_and_execute_query(self, limit = 25, offset = None):
        """
            This functions builds a DiffgramQuery object and executes it with the
            SQLAlchemy executor to get a list of File objects that we can serialized
            and return to the user.
        :return:
        """
        query_string = self.metadata.get('query')
        if not query_string:
            return False, {'error': {'query_string': 'Provide query_string'}}
        query_creator = QueryCreator(session = self.session, project = self.project, member = self.member, directory = self.directory)
        diffgram_query_obj = query_creator.create_query(query_string = query_string)
        if len(query_creator.log['error'].keys()) > 0:
            return False, query_creator.log
        executor = SqlAlchemyQueryExecutor(session = self.session, diffgram_query = diffgram_query_obj)
        sql_alchemy_query, execution_log = executor.execute_query()
        if sql_alchemy_query:
            if limit is not None:
                sql_alchemy_query = sql_alchemy_query.limit(limit)

            if offset:
                sql_alchemy_query = sql_alchemy_query.offset(offset)
            file_list = sql_alchemy_query.all()
        else:
            return False, execution_log
        return file_list, query_creator.log

    def file_view_core(
        self,
        mode = "serialize"):
        """
        mode
            serialize is in context of web, ie serialize the resulting list
                currently defaults to this context
            objects returns the database objects, ie for auto commit

        """
        output_file_list = []
        limit_counter = 0

        file_count = 0  # File count includes ones we don't actually query
        # outside of limits...

        if self.metadata['file_view_mode'] is None or \
            self.metadata['file_view_mode'] not in ["changes", "annotation", "home", "task", "explorer"]:
            return "Invalid file_view_mode", False

        ignore_id_list = None

        # For creating / viewing Jobs

        if self.metadata['file_view_mode'] == "task" and self.metadata['job_id']:

            # TODO permissions check on job id?

            # TODO handling for larger file sizes

            # TODO better null handling here... a lot of assumptions
            # Would prefer to declare "new" job condition
            # Instead of inferring from file_view_mode and job_id being present

            job = Job.get_by_id(session = self.session,
                                job_id = self.metadata['job_id'])

            file_list_attached_to_job = WorkingDirFileLink.file_list(
                session = self.session,
                working_dir_id = job.directory_id,
                limit = None)

            # TODO future maybe just get ids only from sql
            ignore_id_list = [i.id for i in file_list_attached_to_job]

            for index_file_attach, file in enumerate(file_list_attached_to_job):
                file_serialized = file.serialize_with_type(session = self.session)
                output_file_list.append(file_serialized)
                output_file_list[index_file_attach]['attached_to_job'] = True

        ann_is_complete = None
        if self.metadata['annotation_status'] == "Completed":
            ann_is_complete = True
        if self.metadata['annotation_status'] == "Not completed":
            ann_is_complete = False

        has_some_machine_made_instances = None
        if self.metadata['machine_made_setting'] == "Predictions only":
            has_some_machine_made_instances = True

        if self.metadata['machine_made_setting'] == "Human only":
            has_some_machine_made_instances = False

        media_type = self.metadata.get("media_type", None)

        if media_type in ["All", None]:
            media_type_query = ["image", "video", "text"]

        if media_type == "Image":
            media_type_query = "image"

        if media_type == "Video":
            media_type_query = "video"

        exclude_removed = True
        if self.metadata['file_view_mode'] in ["changes"]:
            exclude_removed = False

        job_id = None
        if self.metadata['file_view_mode'] in ["annotation", "home"]:
            # TODO clarify this is in context of viewing Files for a project
            if self.metadata['job_id']:
                job_id = self.metadata['job_id']

        order_by_direction = desc
        requested_direction = self.metadata['pagination'].get('descending')
        if requested_direction == False:  # defaults to true...
            order_by_direction = asc

        # Default
        order_by_class_and_attribute = File.time_last_updated

        requested_order_by = self.metadata['pagination'].get('sortBy')
        if requested_order_by:
            if requested_order_by == "filename":
                order_by_class_and_attribute = File.original_filename
            if requested_order_by == "created_time":
                order_by_class_and_attribute = File.created_time
            if requested_order_by == "time_last_updated":
                order_by_class_and_attribute = File.time_last_updated

        if self.metadata.get('query') and self.metadata.get('query') != '':
            working_dir_file_list, log = self.build_and_execute_query(
                limit = self.metadata["limit"],
                offset = self.metadata["start_index"],
            )
            if not working_dir_file_list or len(log['error'].keys()) > 1:
                return False
        else:
            query, count = WorkingDirFileLink.file_list(
                session = self.session,
                working_dir_id = self.directory.id,
                ann_is_complete = ann_is_complete,
                type = media_type_query,
                return_mode = "query",
                limit = self.metadata["limit"],
                date_from = self.metadata["date_from"],
                date_to = self.metadata["date_to"],
                issues_filter = self.metadata["issues_filter"],
                offset = self.metadata["start_index"],
                original_filename = self.metadata['search_term'],
                order_by_class_and_attribute = File.id,
                order_by_direction = order_by_direction,
                exclude_removed = exclude_removed,
                file_view_mode = self.metadata['file_view_mode'],
                job_id = job_id,
                has_some_machine_made_instances = has_some_machine_made_instances,
                ignore_id_list = ignore_id_list,
                count_before_limit = True
            )

            file_count += count

            working_dir_file_list = query.all()

        if mode == "serialize":
            for index_file, file in enumerate(working_dir_file_list):
                if self.metadata['file_view_mode'] == 'explorer':
                    file_serialized = file.serialize_with_annotations(self.session)
                else:
                    file_serialized = file.serialize_with_type(self.session)
                output_file_list.append(file_serialized)

                limit_counter += 1

        if mode == "objects":
            output_file_list.extend(working_dir_file_list)
            limit_counter += len(working_dir_file_list)

        self.metadata['end_index'] = self.metadata['start_index'] + len(working_dir_file_list)

        # search_info['no_results_match_search'] = True
        self.metadata['length_current_page'] = len(output_file_list)
        self.metadata['file_count'] = file_count

        # TODO not clear why we need this / why this is seperate
        # from file_count
        if limit_counter == 0:
            self.metadata['no_results_match_search'] = True

        return output_file_list


"""
1. Default to start at index 0
2. If a request_next_page is true
2.1 index = previous search -> leave_off_index
"""
