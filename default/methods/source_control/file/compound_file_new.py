import traceback

try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.auth.member import Member
from shared.database.project import Project
from shared.database.input import Input
from sqlalchemy.orm.session import Session
from typing import List
from shared.database.model.model import Model
from shared.database.model.model_run import ModelRun
from shared.annotation import Annotation_Update
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


@routes.route('/api/v1/project/<string:project_string_id>/file/new-compound', methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor", "Viewer"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
def api_file_compound_new(project_string_id):
    """
        Create a new compound file.
       :param project_string_id:
       :return:
       """
    spec_list = [{'name': str},
                 {'directory_id': None},
                 {'type': {
                    'kind': str,
                    'default': 'compound',
                    }},
                 {'instance_list': {
                     'default': [],
                     'kind': list,
                     'allow_empty': True
                 }},

                ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if regular_log.log_has_error(log):
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        project = Project.get_by_string_id(session, project_string_id)
        member = get_member(session)
        file_data, log = file_compound_new_core(
            session = session,
            log = log,
            project = project,
            member = member,
            directory_id = input['directory_id'],
            name = input['name'],
            type = input['type'],
            instance_list = input['instance_list'],
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(file = file_data, log = log), 200


def process_compound_instance_list(session: Session,
                                   project: Project,
                                   instance_list: List[dict],
                                   root_file: File,
                                   member: Member,
                                   log: dict) -> [bool, dict]:
    if len(instance_list) == 0:
        return True, log

    if not root_file.type.startswith('compound'):
        log['error']['root_file'] = 'Root file must be of type compound.'
        return False, log

    models = Model.list(session = session, project_id = project.id)
    model_run_list = ModelRun.list(session = session, project_id = project.id)
    allowed_model_id_list = [m.id for m in models]
    allowed_model_runs_id_list = [m.id for m in model_run_list]
    try:
        annotation_update = Annotation_Update(
            session = session,
            file = root_file,
            instance_list_new = instance_list,
            project_id = project.id,
            video_data = None,
            task = None,
            complete_task = False,
            member = member,
            do_init_existing_instances = False,
            external_map = None,
            external_map_action = None,
            do_update_sequences = False,
            allowed_model_id_list = allowed_model_id_list,
            allowed_model_run_id_list = allowed_model_runs_id_list,
            force_lock = False
        )
        # Propagate errors if any back up to input
        if regular_log.log_has_error(annotation_update.log):
            log['error'] = annotation_update.log['error']
            return False, log
        new_file = annotation_update.main()
        annotation_update.file.set_cache_key_dirty('instance_list')
    except Exception as e:
        trace = traceback.format_exc()
        logger.error(trace)
        log['error']['instance_list_compound'] = trace
        return False, log
    return True, log


def file_compound_new_core(session: Session,
                           project: Project,
                           directory_id: int,
                           name: int,
                           type: str,
                           member: Member,
                           instance_list: List[dict],
                           log: dict = regular_log.default()):
    """
        Creates a new compound file.
    :param session:
    :param project:
    :param directory_id:
    :param name:
    :param member:
    :param log:
    :return:
    """

    dataset = WorkingDir.get_by_id(session = session, directory_id = directory_id)

    if not dataset or dataset.project_id != project.id:
        msg = f'Dataset {directory_id} does not belong to project {project.project_string_id}'
        log['error']['directory_id'] = msg
        return None, log

    existing_file = File.get_by_name_and_directory(session = session,
                                                   directory_id = directory_id,
                                                   file_name = name,
                                                   with_deleted = False)
    if existing_file is not None:
        msg = f'File name: {name} already exists in dataset {dataset.nickname}<id={dataset.id}>'
        log['error']['directory_id'] = msg

        return None, log

    input_obj = Input.new(
        directory_id = directory_id,
        project_id = project.id,
        project = project,
        type = 'from_compound',
        media_type = 'compound',
        instance_list = {'list': instance_list}
    )

    file = File.new(
        session = session,
        working_dir_id = directory_id,
        file_type = type,
        original_filename = name,
        project_id = project.id,  # TODO test if project_id is working as expected here
        input_id = input_obj.id
    )
    input_obj.file_id = file.id
    input_obj.original_filename = name
    input_obj.status = 'base_object_created'
    input_obj.processing_deferred = False
    input_obj.percent_complete = 100
    session.add(input_obj)
    session.flush()
    if len(instance_list) > 0:
        result, log = process_compound_instance_list(
            session = session,
            project = project,
            instance_list = instance_list,
            root_file = file,
            member = member,
            log = log
        )
        if regular_log.log_has_error(log):
            return None, log
    file_data = file.serialize_base_file()
    file_data['input'] = input_obj.serialize()
    return file_data, log
