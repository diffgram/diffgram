try:
    from methods.regular.regular_api import *
except:
    from walrus.methods.regular.regular_api import *
from shared.database.project_migration.project_migration import ProjectMigration
from shared.database.external.external import ExternalMap
from shared.project_migration.ExternalMigrationManager import initialize_migration_threaded


@routes.route('/api/walrus/project/<string:project_string_id>/project-migration/list', methods = ['GET'])
@Project_permissions.user_has_project(["admin"])
def api_project_migration_list(project_string_id):
    """
        Fetches the details of the given project migration ID.
    """

    with sessionMaker.session_scope() as session:
        member = get_member(session)
        log = regular_log.default()
        project_migration_data, log = list_project_migrations_core(
            session,
            log = log,
            project_string_id = project_string_id,
            member = member,
        )

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    return jsonify(project_migration_data), 200


def list_project_migrations_core(session,
                                 project_string_id,
                                 member,
                                 log = regular_log.default()):
    """
        Returns the created discussion as a python dictionary.
    :param session:
    :param project_string_id:
    :param member:
    :param member:
    :param log:
    """
    project = Project.get_by_string_id(session, project_string_id)

    project_migration_list = ProjectMigration.list(session, project.id)

    project_migration_data = [p.serialize() for p in project_migration_list]
    return project_migration_data, log
