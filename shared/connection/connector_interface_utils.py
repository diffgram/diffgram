# OPENCORE - ADD
from shared.database.user import User
from methods.connectors.connectors import ConnectorManager
from shared.connection.connection_operations import Connection_Operations
import datetime


def get_connector(connector_id, session, input=None, check_perms=True):
    connection_operations = Connection_Operations(
        session=session,
        member=None,
        connection_id=connector_id
    )
    connection = connection_operations.get_existing_connection(connector_id)
    if check_perms:
        connection_operations.validate_existing_connection_id_permissions()

    if input is None:
        conn_manager = ConnectorManager(connection=connection, session=session)
        connector_class = conn_manager.get_connector_class()

        auth_data = {
            'endpoint_url': connection.private_host,
            'disabled_ssl_verify': connection.disabled_ssl_verify,
            'client_email': connection.account_email,
            'client_id': connection.private_id,
            'client_secret': connection_operations.get_secret(),
            'project_id': connection.project_id_external,
        }
    else:
        integration_name = input.get('integration_name') if input.get('integration_name') is not None else connection.integration_name
        conn_manager = ConnectorManager(integration_name=integration_name)
        connector_class = conn_manager.get_connector_class()
        auth_data = {
            'endpoint_url': input.get('private_host') if input.get('private_host') is not None else connection.private_host,
            'client_email':  input.get('account_email') if input.get('account_email') is not None else connection.account_email,
            'client_id': input.get('private_id') if input.get('private_id') is not None else connection.private_id,
            'client_secret': input.get('private_secret') if input.get('private_secret') is not None else connection_operations.get_secret(),
            'disabled_ssl_verify': input.get('disabled_ssl_verify') if input.get('disabled_ssl_verify') is not None else connection.disabled_ssl_verify,
            'project_id': input.get('project_id_external') if input.get('project_id_external') is not None else connection.project_id_external,
        }

    config_data = {'project_string_id': connection.project.project_string_id}
    connector = connector_class(auth_data=auth_data, config_data=config_data)

    if len(connection_operations.log["error"].keys()) >= 1:
        return connection_operations.log, False

    return connector, True


def add_event_data_to_input(input, session, connector_id):
    user = User.get_current_user(session)
    input['opts']['event_data'] = {
        'request_user': user.id,
        'date_time': datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S'),
        'connection_id': connector_id
    }
    return input
