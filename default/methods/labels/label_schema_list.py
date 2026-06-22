# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

# Import necessary classes and functions for working with the database and handling HTTP requests
from shared.database.discussion.discussion import Discussion
from shared.database.discussion.discussion_comment import DiscussionComment
from sqlalchemy.orm.session import Session
from shared.database.auth.member import Member
from shared.database.labels.label_schema import LabelSchema


@routes.route('/api/v1/project/<string:project_string_id>/labels-schema', methods = ['GET'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor", "Viewer", "allow_if_project_is_public"],
                                      apis_user_list = ["api_enabled_builder"])
def api_label_schema_list(project_string_id: str):
    """
        This function handles the GET request for fetching all label schemas of a given project.

    :param project_string_id: The unique string ID of the project.
    :return: A JSON response containing the list of label schemas or an error message.
    """
    with sessionMaker.session_scope() as session:
        project = Project.get_by_string_id(session, project_string_id)
        member = get_member(session)
        log = regular_log.default()

        # Call the core function to fetch the label schemas
        label_schema_data, log = label_schema_list_core(
            session = session,
            project = project,
            member = member,
            log = log,
        )

        # If there are any errors, return a Bad Request status with the error log
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        # Return the list of label schemas as a JSON response with a 200 status
        return jsonify(label_schema_data), 200


def label_schema_list_core(session: Session,
                           project: Project,
                           member: Member,
                           log = regular_log.default(),
                           is_default = None) -> [list, dict]:
    """
        This function fetches all the label schemas of the given project.

    :param session: The database session object.
    :param project: The project object.
    :param member: The member object.
    :param log: The log object for error handling.
    :param is_default: Optional parameter to filter label schemas by default status.
    :return: A tuple containing the list of label schemas and the log object.
    """
    result = []

    # Fetch the label schemas from the database based on the provided parameters
    schema_list = LabelSchema.list(
        session = session,
        project_id = project.id,
        is_default = is_default
    )

    # Serialize the fetched label schemas and store them in the result list
    result = [s.serialize() for s in schema_list]

    # Return the result list and the log object
    return result, log
