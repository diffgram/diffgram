# This file is a part of OpenCore and contains functions for adding routes related to project-specific functionality.

from methods.regular.regular_api import *  # Importing all functions from the regular_api module


@routes.route('/api/project/<string:project_string_id>/view', methods=['GET'])
@Project_permissions.user_has_project(["allow_if_project_is_public", "admin", "annotator", "Editor", "Viewer"])
def project_view(project_string_id):
    """
    This function handles GET requests to view project details.

    Args:
        project_string_id (str): The unique identifier of the project in string format.

    Returns:
        A JSON response containing the project details and user permission level if logged in.
        200 HTTP status code and Content-Type header set to 'application/json'.

    Raises:
        400 HTTP status code in case of errors during input validation.
    """

    # ... (code continues)


@routes.route('/api/project/<string:project_string_id>/checks', methods=['POST'])
@Project_permissions.user_has_project(["allow_if_project_is_public", "admin", "Editor", "Viewer"])
def project_checks_view(project_string_id):
    """
    This function handles POST requests to perform checks on a specific project directory.

    Args:
        project_string_id (str): The unique identifier of the project in string format.

    Returns:
        A JSON response containing the result of the checks.
        200 HTTP status code and Content-Type header set to 'application/json'.

    Raises:
        400 HTTP status code in case of errors during input validation or if no directory is found.
    """

    # ... (code continues)


@routes.route('/api/project/<string:project_string_id>/transaction/ml/training/estimate', methods=['GET'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer"])
def project_ml_estimate_view(project_string_id):
    """
    This function handles GET requests to estimate the cost and time for ML training in a project.

    Args:
        project_string_id (str): The unique identifier of the project in string format.

    Returns:
        A JSON response containing the estimated cost and time for ML training.
        200 HTTP status code and Content-Type header set to 'application/json'.

    Raises:
        400 HTTP status code in case the project is not found.
    """

    # ... (code continues)


@routes.route('/api/project/<string:project_string_id>/branch/list', methods=['GET'])
@Project_permissions.user_has_project(["allow_if_project_is_public", "admin", "Editor", "Viewer"])
def branch_list_view(project_string_id):
    """
    This function handles GET requests to retrieve the list of branches for a specific project.

    Args:
        project_string_id (str): The unique identifier of the project in string format.

    Returns:
        A JSON response containing the list of branches for the specified project.
        200 HTTP status code and Content-Type header set to 'application/json'.

    Raises:
        400 HTTP status code in case the project is not found.
    """

    # ... (code continues)


@routes.route('/api/project/<string:project_string_id>/annotation_project/checks', methods=['GET'])
@Project_permissions.user_has_project(["admin"])
def annotation_project_view(project_string_id):
    """
    This function handles GET requests to perform checks on an annotation project.

    Args:
        project_string_id (str): The unique identifier of the project in string format.

    Returns:
        A JSON response containing the result of the checks.
        200 HTTP status code and Content-Type header set to 'application/json'.

    Raises:
        400 HTTP status code in case the project is not found.
    """

    # ... (code continues)
