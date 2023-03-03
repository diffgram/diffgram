# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.data_tools_core import Data_tools
from shared.database.export import Export
from shared.export.export_utils import check_export_permissions_and_status
from shared.export.export_view import export_view_core
from shared.regular import regular_log
from flasgger import swag_from
data_tools = Data_tools().data_tools


@routes.route('/api/walrus/project/<string:project_string_id>' +
              '/export/working_dir/list',
              methods=['GET'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer"])
@swag_from('../../docs/export_list.yml')
def export_list(project_string_id):
    """

    Caution:
    This does it for all working dirs in project?
    ie doesn't do it for a single working dir

    """

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        # TODO attach export list to File in source control
        # So it can follow project

        export_list = session.query(Export).filter(
            Export.project_id == project.id,
            Export.archived == False).order_by(
            Export.id.desc()).all()

        export_list_serialized = []
        if export_list:
            for export in export_list:
                export_list_serialized.append(export.serialize())

    out = jsonify(success=True,
                  export_list=export_list_serialized)
    return out, 200


@routes.route('/api/walrus/project/<string:project_string_id>' + '/export/link', methods=['POST'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer"])
def export_link(project_string_id):
    """

    return mode

    return_type, string in ['url', 'data']

    That's why it's 'data' because the "FORMAT" could be JSON too.


    """
    spec_list = [
        {"id": int},
        {"format": {
            'default': 'JSON',
            'kind': str,
            'valid_values_list': ['JSON', 'YAML']
        }
        },
        {"return_type": {
            'default': 'url',
            'kind': str,
            'valid_values_list': ['url', 'data']
        }
        }
    ]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        export = session.query(Export).filter(
            Export.id == input['id']).first()

        export_check_result = check_export_permissions_and_status(export, project_string_id, session)
        if regular_log.log_has_error(export_check_result):
            return jsonify(export_check_result), 400

        result = export_view_core(
            export=export,
            format=input['format'],
            return_type=input['return_type'])

        return jsonify(result), 200

@routes.route('/api/walrus/project/<string:project_string_id>' +
              '/export/<int:export_id>/status',
              methods=['GET'])
@Project_permissions.user_has_project(["admin", "Editor"])
def export_status(project_string_id, export_id):
    """
    Gets status on annotation generation
    """
    if project_string_id is None:
        return "project_string_id is None", 400

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        export = session.query(Export).filter(
            Export.id == export_id).first()

        if not export or export.project_id != project.id:
            return "Security error, invalid match", 400

        out = jsonify(success=True,
                      export=export.serialize())

        return out, 200, {'ContentType': 'application/json'}


@routes.route('/api/walrus/project/<string:project_string_id>' +
              '/export/update',
              methods=['POST'])
@Project_permissions.user_has_project(["admin", "Editor"])
def export_update(project_string_id):
    """
    Update Export
    """
    spec_list = [
        {"id": int},
        {"mode": {
            'kind': str,
            'valid_values_list': ["ARCHIVE"]
        }
        }
    ]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        export = session.query(Export).filter(
            Export.id == input['id']).first()

        if not export or export.project_id != project.id:
            return "Security error, invalid match", 400

        if input['mode'] == "ARCHIVE":
            archive_export(session, export)
            log['success'] = True

        return jsonify(log), 200


def archive_export(session, export):
    export.archived = True
    session.add(export)
