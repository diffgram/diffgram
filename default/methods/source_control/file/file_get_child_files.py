try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.auth.member import Member
from shared.database.project import Project
from sqlalchemy.orm.session import Session
from typing import List
from shared.permissions.policy_engine.policy_engine import PolicyEngine
from shared.database.permissions.roles import ValidObjectTypes
from shared.database.source_control.file import FilePermissions
@routes.route('/api/v1/project/<string:project_string_id>/file/<int:parent_file_id>/child-files', methods = ['GET'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor", "Viewer", "allow_if_project_is_public"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
def api_file_get_child_files(project_string_id: str, parent_file_id: int):
    """
           List all the comments of the given discussion_id

       :param project_string_id:
       :param file_id:
       :return:
       """
    # For now, no filters needed. But might add in the future.
    log = regular_log.default()
    with sessionMaker.session_scope() as session:
        project = Project.get_by_string_id(session, project_string_id)
        member = get_member(session)
        policy_engine = PolicyEngine(session = session, project = project)
        perm_result = policy_engine.member_has_perm(
            object_id = parent_file_id,
            object_type = ValidObjectTypes.file,
            perm = FilePermissions.file_view,
            member = member
        )
        if not perm_result.allowed:
            log['error']['unauthorized'] = f'Missing permissions {FilePermissions.file_view.value} for file {parent_file_id}'
            return jsonify(log = log), 401
        child_files_data, log = get_child_files_core(
            session = session,
            log = log,
            project = project,
            parent_file_id = parent_file_id,
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(child_files = child_files_data, log = log), 200


def get_child_files_core(session: Session,
                         project: Project,
                         parent_file_id: int,
                         log: dict = regular_log.default()) -> [List[dict], dict]:
    """
        Gets the child files of a compound parent file.
    :param session:
    :param project:
    :param parent_file_id:
    :param member:
    :param log:
    :return:
    """

    file = File.get_by_id(session = session, file_id = parent_file_id)
    if file.project_id != project.id:
        log['error']['file_id'] = 'File does not belong to project'
        return None, log
    child_files = file.get_child_files(session = session)
    result = []
    for child in child_files:
        serialized_child_file = child.serialize_with_type(session = session)
        result.append(serialized_child_file)
    return result, log
