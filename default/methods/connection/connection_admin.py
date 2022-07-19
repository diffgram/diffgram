# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

from shared.permissions.super_admin_only import Super_Admin
from shared.database.connection.connection import Connection
from shared.connection.connection_operations import Connection_Operations


@routes.route('/api/v1/connection/info/<int:connection_id>',
              methods = ['GET'])
@General_permissions.grant_permission_for(['normal_user'])
def connection_info_api(connection_id):
    """
    Permissions handled by connection_Runner
    """

    with sessionMaker.session_scope() as session:
        connection_operations = Connection_Operations(
            session = session,
            member = None,
            connection_id = connection_id
        )

        if len(connection_operations.log["error"].keys()) >= 1:
            return jsonify(log = connection_operations.log), 400

        connection_operations.get_existing_connection(connection_id)

        connection_operations.validate_existing_connection_id_permissions()

        connection_operations.log['success'] = True

        return jsonify(
            log = connection_operations.log,
            connection = connection_operations.connection.serialize()), 200


@routes.route('/api/v1/connection/save',
              methods = ['POST'])
@General_permissions.grant_permission_for(['normal_user'])
def connection_save_api():
    """
    May or may not have an ID if it's new.

    I think it's safe for save to be different from running it.

    metadata
        meaning it's data one level removed from actual connection
        ie how the connection should be structured

    """
    spec_list = [
        {"connection_id": {
            'kind': int,
            'required': False  # (ie for first save)
        }
        },
        {'connection': dict}  # see connection_spec for spec
    ]
    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400
    with sessionMaker.session_scope() as session:
        connection_operations = Connection_Operations(
            session = session,
            member = None,
            connection_id = input['connection_id'],
            metadata = input['connection']
        )

        if len(connection_operations.log["error"].keys()) >= 1:
            return jsonify(log = connection_operations.log), 400

        connection_operations.validate_connection_permissions_scope(
            permission_scope = input['connection'].get('permission_scope'),
            project_string_id = input['connection'].get('project_string_id')
        )

        connection_operations.save()

        if len(connection_operations.log["error"].keys()) >= 1:
            return jsonify(log = connection_operations.log), 400

        connection_operations.log['success'] = True

        return jsonify(
            log = connection_operations.log,
            connection = connection_operations.connection.serialize()), 200


@routes.route('/api/project/<string:project_string_id>/connections', methods = ['GET'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer", "allow_if_project_is_public"])
def connection_list_api(project_string_id):
    """
    security model assumes that validate_connection_permissions_permission_scope
    checks it / returns forbidden if not applicable.

    """
    log = regular_log.default()
    with sessionMaker.session_scope() as session:
        ### MAIN ###
        connection_operations = Connection_Operations(
            session = session,
            member = None
        )

        if len(connection_operations.log["error"].keys()) >= 1:
            return jsonify(log = connection_operations.log), 400

        connection_operations.validate_connection_permissions_scope(
            permission_scope = "project",
            project_string_id = project_string_id,
        )
        # Curious if we want a connection "grouping" concept or not

        connection_list = connection_operations.connection_list()

        connection_list_serialized = []
        for connection in connection_list:
            connection_list_serialized.append(connection.serialize())

        log['success'] = True

        return jsonify(connection_list = connection_list_serialized,
                       log = connection_operations.log), 200
