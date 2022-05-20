# OPENCORE - ADD
from methods.regular.regular_api import *
from methods.connectors.connector_interface_utils import get_connector  , add_event_data_to_input


@routes.route('/api/walrus/v1/connectors/<int:connector_id>/fetch-data', methods=['POST'])
@General_permissions.grant_permission_for(['normal_user'])
def fetch_data(connector_id):
    spec_list = [{'opts': dict}, {'project_string_id': str}]

    log, input_data, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)

    with sessionMaker.session_scope() as session:
        connector, success = get_connector(connector_id, session)
        if not success:
            return jsonify(connector), 400

        # Add relevant data to opts
        input_data = add_event_data_to_input(input_data, session, connector_id)
        connection_result = connector.connect()
        if 'log' in connection_result:
            return jsonify(connection_result), 400

        result = connector.fetch_data(input_data['opts'])
        if 'log' in result:
            return jsonify(result), 400

        return jsonify(result), 200


@routes.route('/api/walrus/v1/connectors/<int:connector_id>/put-data', methods=['POST'])
@General_permissions.grant_permission_for(['normal_user'])
def put_data(connector_id):
    spec_list = [{'opts': dict}, {'project_string_id': str}]

    log, input_data, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)

    with sessionMaker.session_scope() as session:
        connector, success = get_connector(connector_id, session)
        if not success:
            return jsonify(connector), 400

        # Add relevant data to opts
        input_data = add_event_data_to_input(input_data, session, connector_id)
        connection_result = connector.connect()
        if 'log' in connection_result:
            return jsonify(connection_result), 400

        result = connector.put_data(input_data['opts'])
        if 'log' in result:
            return jsonify(result), 400

        return jsonify(result), 200


@routes.route('/api/walrus/v1/connection/test',
              methods=['POST'])
@General_permissions.grant_permission_for(['normal_user'])
def test_connection_api():
    """

    """
    spec_list = [
        {
            "connection_id": {
                'kind': int,
                'required': False
            }
        },
        {
            "project_string_id": {
                'kind': str,
                'default': None,
                'required': True
            },
        },
        {
            'integration_name': {
                'kind': str,
                'integration_name': None,
                'required': False
            }
        },
        {
            'permission_scope': {
                'default': 'project',
                'kind': str,
                'required': False,
                'valid_values_list': ['project', 'org']
            }
        },
        {
            'private_host': {
                'default': None,
                'kind': str,
                'required': False,
            }
        },
        {
            'private_id': {
                'default': None,
                'kind': str,
                'required': False,
            }
        },
        {
            'private_secret': {
                'default': None,
                'kind': str,
                'required': False,
            }
        },
        {
            'disabled_ssl_verify': {
                'default': None,
                'kind': bool,
                'required': False,
            }
        },
        {
            'account_email': {
                'default': None,
                'kind': str,
                'required': False,
            }
        },
        {
            'project_id_external': {
                'default': None,
                'kind': str,
                'required': False,
            }
        }
    ]

    log, input, untrusted_input = regular_input.master(
        request=request,
        spec_list=spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400
    
    with sessionMaker.session_scope() as session:
        connector, success = get_connector(input['connection_id'], session, input)
        if not success:
            return jsonify(connector), 400

        connection_result = connector.test_connection()
        if "log" in connection_result and len(connection_result["log"]["error"].keys()) >= 1:
            return jsonify(connection_result), 400
        log['success'] = True
        return jsonify(connection_result), 200
