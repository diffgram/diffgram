# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.source_control.working_dir import VALID_ACCESS_TYPES
from shared.database.user import UserbaseProject
from shared.database.permissions.roles import RoleMemberObject, ValidObjectTypes
from shared.database.source_control.dataset_perms import DatasetDefaultRoles


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/directory/new',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("200000 per day")
def new_directory_api(project_string_id):
    """


    """
    spec_list = [{"nickname": str}, {"access_type": str}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        ### MAIN
        nickname = input["nickname"]
        access_type = input.get('access_type', 'project')
        project = Project.get(session = session,
                              project_string_id = project_string_id)

        count_existing = Project_Directory_List.get_by_project(
            session = session,
            project_id = project.id,
            exclude_archived = True,
            kind = "counts"
        )
        if access_type not in VALID_ACCESS_TYPES:
            log['error']['access_type'] = f'Invalid access type. Must be one of {VALID_ACCESS_TYPES}'
            return jsonify(log = log), 400
        if count_existing >= 200000:
            log['error']["limit"] = "Limit of directories. " + \
                                    "Please archive a directory or upgrade plan or contact us."
            return jsonify(log = log), 400

        existing_name_count = Project_Directory_List.get_by_project(
            session = session,
            project_id = project.id,
            exclude_archived = True,
            kind = "counts",
            nickname = nickname
        )

        # logger.info(("existing_name", existing_name_count))

        if existing_name_count != 0:
            log['error']["name"] = "Existing with same name in project."
            return jsonify(log = log), 400

        directory = WorkingDir.new_blank_directory(
            session = session,
            nickname = nickname,
            project_id = project.id,
            project_default = False,
            access_type = access_type
        )

        Project_Directory_List.add(
            session = session,
            working_dir_id = directory.id,
            project_id = project.id,
            nickname = nickname
        )
        member = get_member(session)
        RoleMemberObject.new(
            session = session,
            object_type = ValidObjectTypes.dataset,
            object_id = directory.id,
            member_id = member.id,
            default_role_name = DatasetDefaultRoles.dataset_admin
        )

        project.set_cache_key_dirty('directory_list')
        session.add(project)

        user_email = None
        member_id = None
        user = User.get(session)
        if user:
            user_email = user.email
            member_id = user.member_id

        Event.new(
            kind = "new_directory",
            session = session,
            member_id = member_id,
            success = True,
            project_id = project.id,
            email = user_email
        )
        ####

        session.flush()  # to get id
        log['success'] = True
        out = jsonify(log = log,
                      new_directory = directory.serialize())
        return out, 200
