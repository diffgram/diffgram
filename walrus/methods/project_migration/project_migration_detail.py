try:
    from methods.regular.regular_api import *
except:
    from walrus.methods.regular.regular_api import *
from shared.database.project_migration.project_migration import ProjectMigration
from shared.database.external.external import ExternalMap
from shared.project_migration.ExternalMigrationManager import initialize_migration_threaded


@routes.route('/api/walrus/project/<string:project_string_id>/project-migration/<string:project_migration_id>', methods = ['GET'])
@Project_permissions.user_has_project(["admin"])
def api_project_migration_detail(project_string_id, project_migration_id):
    """
        Fetches the details of the given project migration ID.
    """

    with sessionMaker.session_scope() as session:
        member = get_member(session)
        log = regular_log.default()
        project_migration_data, log = new_project_migration_core(
            session,
            log = log,
            project_migration_id = project_migration_id,
            project_string_id = project_string_id,
            member = member,
        )

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    return jsonify(project_migration_data), 200


def new_project_migration_core(session,
                               project_migration_id,
                               project_string_id,
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
    project = Project.get_by_string_id(session,project_string_id)

    project_migration = ProjectMigration.get_by_id(session, project_migration_id)
    if project_migration.project_id != project.id:
        log['error']['project_id'] = 'Project migration does not belong to this project.'
        return None, log
    project_migration_data = project_migration.serialize()
    return project_migration_data, log
