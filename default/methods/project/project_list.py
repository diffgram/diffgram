# OPENCORE - ADD
from methods.regular.regular_api import *

import datetime
from shared.permissions.general import General_permissions
from shared.permissions.super_admin_only import Super_Admin


@routes.route('/api/v1/project/list',
              methods = ['POST'])
@General_permissions.grant_permission_for(['normal_user', 'super_admin'])
def project_list_api():
    spec_list = [{'username': None}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        # TODO this is a placeholder for future thing of getting projects
        # by username
        # But for now default case is getting logged in users project
        # So we just use User.get()

        user = User.get(session = session)

        project_list = project_list_core(session = session,
                                         user = user)

        log['success'] = True
        return jsonify(log = log,
                       project_list = project_list), 200


def project_list_core(session,
                      user):
    project_list = Project.list(
        user = user,
        session = session)

    out_list = []

    for project in project_list:
        out_list.append(project.serialize(session = session))

    return out_list


"""
Not sure on trade offs here of having this as a separate method...
Benefit is more isolation. For example a super admin flag for regular API doesn't make sense?
Downside is code duplication.
Not sure what the concerns is about conditioning on being super admin if we do it elsewhere

I guess part of question here is if we really want this as an "admin" thing or 
want to be able to "inspect" / go to projects from it/ analyize projects in more ways...

Also not clear about this vs integrations with other stuff, ie like you are already sending 
events to other services...

Other thing is the more "generic" search method for project is based on user object at the moment...
Perhaps user should be passed as an option to a more generic method on Project itself...

"""


@routes.route('/api/v1/admin/project/list',
              methods = ['POST'])
@Super_Admin.is_super()
def project_list_super_admin_api():
    # Could put other search options here...
    spec_list = [
        {"limit": {
            'kind': int,
            'default': 25
        }
        }]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project_list = Project.list(
            mode = "super_admin",
            session = session,
            limit = input['limit']
        )

        out_list = []

        for project in project_list:

            out_list.append(project.serialize(session))

        log['success'] = True
        return jsonify(log = log,
                       project_list = out_list), 200
