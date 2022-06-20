try:
    from methods.regular.regular_api import *
except:
    from walrus.methods.regular.regular_api import *
from shared.database.project_migration.project_migration import ProjectMigration
from shared.database.external.external import ExternalMap
from shared.project_migration.ExternalMigrationManager import initialize_migration_threaded
from shared.connection.connection_operations import Connection_Operations


@routes.route('/api/walrus/project/<string:project_string_id>/project-migration/new', methods = ['POST'])
@limiter.limit("300 per second")
@Project_permissions.user_has_project(["admin"])
def api_new_project_migration(project_string_id):

    spec_list = [
        {"labelbox_project_id": {
            'kind': str,
            'default': None,
            'required': False
            }
        },
        {"connection_id": {
            'kind': int,
            'default': None,
            'required': True
            }
        },
        {"import_schema": {
            'kind': bool,
            'default': True,
            'required': True
            }
        },
        {"import_files": {
            'kind': bool,
            'default': False,
            'required': True
            }
        },
        {"id": {
            'kind': int,
            'default': None,
            'required': False
            }
        },
        {"label_schema_id": {
            'kind': int,
            'default': None,
            'required': False
            }
        }
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        project = Project.get_by_string_id(session = session, project_string_id = project_string_id)

        label_schema_id = input['label_schema_id']
        if label_schema_id:
            schema = LabelSchema.get_by_id(session, 
                                           label_schema_id, 
                                           project_id = project.id)
            if schema is None:
                log['error']['schema_id'] = 'Schema does not exist or does not belong to project'
                return jsonify(log = log), 400
        else:
            schema = LabelSchema.get_default(session, project_id = project.id)

        connection_id = input['connection_id']
        connection_operations = Connection_Operations(
            session = session,
            member = None,
            connection_id = connection_id
        )

        if len(connection_operations.log["error"].keys()) >= 1:
            return jsonify(log = connection_operations.log), 400

        connection_operations.get_existing_connection(connection_id)
        connection_operations.validate_existing_connection_id_permissions()


        member = get_member(session)
        eventhub_data, log = new_project_migration_core(
            session,
            log = log,
            labelbox_project_id = input['labelbox_project_id'],
            connection_id = connection_id,
            import_schema = input['import_schema'],
            import_files = input['import_files'],
            existing_migration_id = input['id'],
            project_string_id = project_string_id,
            member = member,
            label_schema_id=schema.id
        )

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    return jsonify(eventhub_data), 200


def new_project_migration_core(session,
                               labelbox_project_id,
                               project_string_id,
                               connection_id,
                               import_schema,
                               import_files,
                               existing_migration_id,
                               member,
                               log = regular_log.default(),
                               label_schema_id=None):
    """
        Returns the created discussion as a python dictionary.
    :param session:
    :param log:
    :param member:
    :param project:
    :param title:
    :param description:
    :param attached_elements:
    :return: created discussion python dict.
    """

    if existing_migration_id:
        project_migration = ProjectMigration.get_by_id(session, existing_migration_id)
        initialize_migration_threaded(project_migration.id)
        project_migration_data = project_migration.serialize()
        return project_migration_data, log

    project = Project.get_by_string_id(session = session, project_string_id = project_string_id)
    external_map = ExternalMap.new(
        session = session,
        external_id = labelbox_project_id,
        type = 'labelbox_project_id',
        diffgram_class_string = 'project',
        project = project,
        add_to_session = True,
        flush_session = True
    )

    project_migration = ProjectMigration.new(
        session = session,
        connection_id = connection_id,
        import_files = import_files,
        import_schema = import_schema,
        member_created_id = member.id,
        project_id = project.id,
        external_mapping_project_id = external_map.id,
        description = f'Labelbox Project ID: {labelbox_project_id}',
        label_schema_id = label_schema_id
    )
    regular_methods.commit_with_rollback(session)
    initialize_migration_threaded(project_migration.id)

    project_migration_data = project_migration.serialize()
    return project_migration_data, log
