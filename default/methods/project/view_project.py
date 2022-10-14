# OPENCORE - ADD
from methods.regular.regular_api import *


@routes.route('/api/project/<string:project_string_id>/view',
              methods = ['GET'])
@Project_permissions.user_has_project(["allow_if_project_is_public",
                                       "admin",
                                       "Editor",
                                       "Viewer"])
def project_view(project_string_id):
    """

    """

    with sessionMaker.session_scope() as session:
        project = Project.get_project(session, project_string_id)

        if project.deletion_pending == True:
            return jsonify("Project scheduled for deletion"), 200

        if project is not None:
            # not super happy with permission thing being here

            # If the project is public and use is not logged in
            # there won't be a permission to attach here right?
            user = User.get(session)
            user_permission_level = None
            if user:
                user_permission_level = user.serialize_with_permission_only(project_string_id)

            # TODO move this into Project class?
            if project.is_public is True:
                project_serialized = project.serialize_public(session)
            else:
                project_serialized = project.serialize()
            ###

            out = jsonify(user_permission_level = user_permission_level,
                          project = project_serialized)
        else:
            out = jsonify({"none_found": True})

        return out, 200, {'ContentType': 'application/json'}


@routes.route('/api/project/<string:project_string_id>/checks',
              methods = ['POST'])
@Project_permissions.user_has_project(
    ["allow_if_project_is_public", "admin", "Editor", "Viewer"])
def project_checks_view(project_string_id):
    """

    """
    spec_list = [{"directory_id": int}]
    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get_project(session, project_string_id)

        directory = WorkingDir.get_with_fallback(
            session = session,
            directory_id = input['directory_id'],
            project = project)

        if directory is False:
            log['error']['directory'] = "No directory found"
            return jsonify(log = log), 400

        out = jsonify({})

        return out, 200


@routes.route('/api/project/<string:project_string_id>/transaction/ml/training/estimate',
              methods = ['GET'])
@Project_permissions.user_has_project(["admin",
                                       "Editor",
                                       "Viewer"])
def project_ml_estimate_view(project_string_id):
    """

    """

    with sessionMaker.session_scope() as session:
        project = Project.get_project(session, project_string_id)

        if project is not None:

            # Temp estimate here since we aren't using ml transactions

            new_estimate = {
                "costs": {
                    "Standard": 1
                },
                "time": {
                    "Standard": 90
                }
            }

            out = jsonify(success = True,
                          new_estimate = new_estimate)
        else:
            out = jsonify({"none_found": True})

        return out, 200, {'ContentType': 'application/json'}


@routes.route('/api/project/<string:project_string_id>/branch/list',
              methods = ['GET'])
@Project_permissions.user_has_project(["allow_if_project_is_public",
                                       "admin",
                                       "Editor",
                                       "Viewer"])
def branch_list_view(project_string_id):
    """

    """

    with sessionMaker.session_scope() as session:
        project = Project.get_project(session, project_string_id)

        if project is not None:

            out = jsonify(branch_list = project.serialize_branch_list())
        else:
            out = jsonify({"none_found": True})

        return out, 200, {'ContentType': 'application/json'}


@routes.route('/api/project/<string:project_string_id>/annotation_project/checks',
              methods = ['GET'])
@Project_permissions.user_has_project(["admin"])
def annotation_project_view(project_string_id):
    with sessionMaker.session_scope() as s:
        project = Project.get_project(s, project_string_id)

        if project is not None:

            # TODO get cost estimate
            # new_estimate = # something

            out = jsonify(project = project.serialize())
        else:
            out = jsonify({"none_found": True})

        return out, 200, {'ContentType': 'application/json'}
