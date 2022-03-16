try:
    from methods.regular.regular_api import *
except:
    from walrus.methods.regular.regular_api import *
from shared.database.project_migration.project_migration import ProjectMigration
from shared.database.external.external import ExternalMap
from shared.project_migration.ExternalMigrationManager import initialize_migration_threaded


@routes.route('/api/walrus/project-migration/<string:project_string_id>/new', methods = ['POST'])
@limiter.limit("300 per second")
@Project_permissions.user_has_project(["admin"])
def api_new_project_migration(project_string_id):
    """
        Creates a new eventhub entry on based on the POST params.
    """
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
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        member = get_member(session)
        eventhub_data, log = new_project_migration_core(
            session,
            log = log,
            labelbox_project_id = input['labelbox_project_id'],
            connection_id = input['connection_id'],
            import_schema = input['import_schema'],
            import_files = input['import_files'],
            project_string_id = project_string_id,
            member = member,
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
                               member,
                               log = regular_log.default()):
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
        external_mapping_project_id = external_map.id
    )
    session.commit()
    print('MIGRATIONADDD', external_map, external_map.id, project_migration.external_mapping_project, project_migration.external_mapping_project_id)
    initialize_migration_threaded(project_migration.id)

    project_migration_data = project_migration.serialize()
    return project_migration_data, log
