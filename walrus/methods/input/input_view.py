# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.export import Export
from shared.database.input import Input
from sqlalchemy.orm import defer


@routes.route('/api/walrus/v1/project/<string:project_string_id>' +
              '/input/view/list',
              methods = ['POST'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer"])
def input_list_web(project_string_id):
    """

    Show last x number??

    Assumption of showing project wide input?

    Status filter context:
        Better input filtering for debugging / understanding system behavior.
        And for users for larger projects, once there's 100s of inputs a person may only want to see the most recent processing ones, or confirm no failed ones etc...


    """
    spec_list = [
        {"limit": {
            'kind': int,
            'default': 10
        }
        },
        {"show_archived": {
            'kind': bool,
            'default': False
        }
        },
        {"show_deferred": {
            'kind': bool,
            'default': True
        }
        },
        {"status_filter": {
            'kind': str,
            'default': None,
            'valid_values_list': [
                'All', 'Success', 'Failed', 'Processing']
        }
        },
        {"date_from": {
            'kind': 'date',
            'default': None,
            'required': False
        }
        },
        {"date_to": {
            'kind': 'date',
            'default': None,
            'required': False
        }
        },
        {"file_id": {
            'kind': int,
            'default': None,
            'required': False
        }
        },
        {"batch_id": {
            'kind': int,
            'default': None,
            'required': False
        }
        },
        {"task_id": {
            'kind': int,
            'default': None,
            'required': False
        }
        }
    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)
        ### MAIN
        input_list = build_input_list(
            session = session,
            project = project,
            limit = input['limit'],
            show_archived = input['show_archived'],
            show_deferred = input['show_deferred'],
            status_filter = input['status_filter'],
            date_from_string = input['date_from'],
            date_to_string = input['date_to'],
            file_id = input['file_id'],
            batch_id = input['batch_id'],
            task_id = input['task_id']
        )

        input_list_serialized = []
        if input_list:
            for input in input_list:
                input_list_serialized.append(input.serialize())

    ####

    out = jsonify(success = True,
                  input_list = input_list_serialized)
    return out, 200


def build_input_list(
    session,
    project: Project,
    limit: int = 10,
    show_archived: bool = False,
    show_deferred: bool = True,
    status_filter: str = None,
    date_from_string: str = None,
    date_to_string: str = None,
    file_id: int = None,
    batch_id: int = None,
    task_id: int = None):
    """
    TODO put as part of Input class
    """

    # Front end pagination does -1 for All
    if limit == -1:
        limit = 1000

    limit = min(limit, 1000)

    # parent_file_id is to filter out say
    # an input image for a video file
    query = session.query(Input).options(defer('frame_packet_map')).filter(
        Input.project_id == project.id,
        Input.parent_file_id == None)
    if show_deferred is False:
        # By default we show processing deferred
        # Example reason to set it to False
        # is wanting to see ones "actively" processing
        # vs one's in queue.
        # context of large batch jobs
        query = query.filter(Input.processing_deferred == False)

    if status_filter:

        status_filter = status_filter.lower()

        if status_filter in ['success', 'failed']:
            query = query.filter(Input.status == status_filter)

        elif status_filter == "processing":
            query = query.filter(Input.status.notin_(
                ['success', 'failed']))

    # TODO make date generic mix in with option to change attribute used
    if date_from_string:
        date_from_datetime = datetime.datetime.strptime(date_from_string, "%Y-%m-%d")
        query = query.filter(Input.created_time >= date_from_datetime)

    if date_to_string:
        date_to_datetime = datetime.datetime.strptime(date_to_string, "%Y-%m-%d")
        query = query.filter(Input.created_time <= date_to_datetime)

    if show_archived is False:
        query = query.filter(Input.archived == False)

    if batch_id:
        query = query.filter(Input.batch_id == batch_id)

    if file_id:
        query = query.filter(Input.file_id == file_id)

    if task_id:

        related_file_ids_list = Task.get_file_ids_related_to_a_task(
            session = session,
            task_id = task_id,
            project_id = project.id)

        query = query.filter(
            or_(Input.task_id == task_id,
                Input.file_id.in_(related_file_ids_list)))

    input_list = query.order_by(
        Input.id.desc()).limit(limit).all()

    check_for_interrupted_uploads(
        session = session,
        input_list = input_list)

    return input_list


def check_for_interrupted_uploads(
    session,
    input_list: list):
    """
    Context of user starting an upload (ie from UI),
    and navigating away part way through.

    It's assumed that 'from_resumable' ~= UI
    And that if it's still in 'init' then we haven't started
    properly processing the file.

    Processing deferred False in case it's still in init
    but deferred. (which is ok because then we have the file.)

    The concept of not running this on big lists is that
    in general we expect basic cases to run into this
    more then super users, and default to only show 10 most
    recent, so saves computation if we want to show a big list
    for other reasons.

    Manual test case
        Upload a large file
        Expect first value will be low in seconds ie 11 seconds

    TODO in the future,
    if we update the input status every time it gets a chunk
    then we can use a much tighter bound here
    but at the moment it doesn't seem like it

    This also helps limit retry doing silly things when we don't have
    the file.
    """

    # limits

    # ie for length check to not fail can't be None
    if not input_list: return

    # Mabe also add a random int or something
    if len(input_list) >= 20: return

    for input in input_list:

        if not input.time_updated:  # avoid datetime vs None comparison below
            continue

        time_delta: datetime = datetime.datetime.utcnow() - input.time_updated

        allowed_seconds_to_send = 60 * 60  # 60 seconds * 60, 60 minutes

        # type == source
        if input.type == 'from_resumable' and \
            input.status == 'init' and \
            input.processing_deferred == False and \
            time_delta.seconds > allowed_seconds_to_send:
            input.status = "failed"
            input.status_text = "Appears Upload was interrupted. Please retry. " + \
                                "Keep browser open until upload is complete."
            session.add(input)


@routes.route('/api/walrus/project/<string:project_string_id>' +
              '/export/<int:export_id>/status',
              methods = ['GET'])
@Project_permissions.user_has_project(["admin", "Editor"])
def api_export_status(project_string_id, export_id):
    """
    Gets status on annotation generation
    """
    if project_string_id is None:
        return "project_string_id is None", 400

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        export = session.query(Export).filter(
            Export.id == export_id).first()

        if export.project_id != project.id:
            return "Security error, invalid match", 400

        out = jsonify(success = True,
                      export = export.serialize())

        return out, 200, {'ContentType': 'application/json'}
