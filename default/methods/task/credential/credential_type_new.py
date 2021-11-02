from methods.regular.regular_api import *

from shared.database.task.job.job import Job
from methods.source_control import working_dir  # rename new to directory in the future

from shared.database.task.credential.credential_type import Credential_Type


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/credential/type/new',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("3 per day")
def new_credential_type_api(project_string_id):
    """


    """
    spec_list = [{"name": str},
                 {"description_markdown": str}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        ### MAIN
        user = User.get(session)
        member = user.member

        name = input["name"]
        description_markdown = input["description_markdown"]

        project = Project.get(session = session,
                              project_string_id = project_string_id)

        credential_type = new_core(
            session = session,
            member = member,
            project = project,
            name = name,
            description_markdown = description_markdown)
        ####

        session.flush()  # to get id

        log['success'] = True
        out = jsonify(log = log,
                      credential_type = credential_type.serialize_for_list_view())
        return out, 200


def new_core(session,
             member,
             project,
             name,
             description_markdown):
    """


    """

    credential_type = Credential_Type(
        member_created = member,
        name = name,
        project = project,
        description_markdown = description_markdown)
    session.add(credential_type)

    user_email = None
    user = member.user
    if user:
        user_email = user.email

    Event.new(
        kind = "new_credential",
        session = session,
        member_id = member.id,
        success = True,
        email = user_email
    )

    return credential_type
