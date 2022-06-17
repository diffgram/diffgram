import random
import string

from flask import request
from flask import jsonify

from shared.database import hashing_functions
from methods import routes

from shared.database.project import Project
from shared.database.source_control.file import File
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.database.source_control.working_dir import WorkingDir

from shared.permissions.project_permissions import Project_permissions

from shared.helpers import sessionMaker
from shared.database.labels.label_schema import LabelSchema
from shared.regular import regular_log


# ADDING new view functions here?
# TODO merge old view functions from labels.py


@routes.route('/api/v1/project/<string:project_string_id>' + \
              '/labels/view/name_to_file_id',
              methods = ['GET'])
@Project_permissions.user_has_project(
    ["admin", "Editor", "Viewer", "allow_if_project_is_public"])
def web_build_name_to_file_id_dict(project_string_id):
    """
    """

    log = regular_log.default()
    schema_id = request.args.get('schema_id')

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        name_to_file_id, log = build_name_to_file_id_dict(
            session = session,
            project = project,
            schema_id = schema_id,
            log = log)

        if regular_log.log_has_error(log):
            return jsonify(log), 400
        else:
            log["success"] = True

    return jsonify(log = log,
                   name_to_file_id = name_to_file_id), 200


def build_name_to_file_id_dict(
        session, 
        project, 
        log, 
        schema_id = None):


    if schema_id is None:
        schema = project.get_default_schema(session = session)
        schema_id = schema.id
    else:
        schema = LabelSchema.get_by_id(session = session, id = schema_id, project_id = project.id)
        if not schema:
            log['error']['schema'] = 'Label Schema not found'
            return None, log
        if schema.project_id != project.id:
            log['error']['schema'] = 'Schema does not belong to project.'
            return None, log

    label_file_list = project.get_label_list(
        session = session,
        directory = project.directory_default,
        schema_id = schema_id)

    out = {}

    for elm in label_file_list:
        out[elm['label']['name']] = elm['id']

    return out, log
