# OPENCORE - ADD
from methods.regular.regular_api import *

from shared.database.source_control.file import File
from shared.utils import job_dir_sync_utils
from shared.database.source_control.working_dir import WorkingDirFileLink



@routes.route('/api/v1/project/<string:project_string_id>' +
              '/directory/update',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
@limiter.limit("100 per day")
def update_directory_api(project_string_id):
    """


    """
    spec_list = [
        {"nickname": None},
        {"directory_id": int},
        {"mode": str}
    ]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        # TODO logging edits?

        log = update_directory_core(
            session=session,
            project=project,
            nickname=untrusted_input.get("nickname", None),
            mode=input['mode'],
            directory_id=input['directory_id'],
            log=log
        )

        if len(log["error"].keys()) >= 1:
            return jsonify(log=log), 400

        log['success'] = True
        return jsonify(
            log=log), 200


def update_directory_core(
        session,
        project,
        nickname,
        mode,
        directory_id,
        log
):
    """
    TODO thoughts on options to "promote" a directory to default
    or "jump to" a directory for a user based on prior one they looked at?
    (This second idea would perhaps be better in a different area of code
    note sure)
    """

    directory = WorkingDir.get(
        session=session,
        directory_id=directory_id,
        project_id=project.id)

    if directory is None:
        log['error'] = "No directory found"
        return log

    session.add(directory)

    link = Project_Directory_List.link(
        session=session,
        working_dir_id=directory.id,
        project_id=project.id
    )

    session.add(link)

    if mode == "RENAME":

        if not nickname:
            log['error'] = "No nickname provided"
            return log

        directory.nickname = nickname
        link.nickname = nickname
        log['info'] = "Updated Nickname."
        project.set_cache_key_dirty(cache_key="directory_list")

        return log

    if mode == "ARCHIVE":

        if directory.id == project.directory_default_id:
            """
            We may swap default directory to a different one.
            Context that prior we just rejected request
            But in a larger project, especially created from 
            SDK, the default dir just sits there and it make it look funny
            (especailly since we don't have say counts per dir or
             that other type of stuff yet.)
            """

            project_directory_list = Project_Directory_List.get_by_project(
                session=session,
                project_id=project.id,
                kind="objects",
                exclude_archived=True,
                directory_ids_to_ignore_list=[directory.id]
            )
            if len(project_directory_list) >= 1:
                """
                Realize that labels rely on project default directory
                so dn't allow this to change yet
                But can still hide directory if other stuff is not there...
                Not 100% clear what the side effects of not having a defualt dir
                are will have to search it. 
                more to think about to do this well
                ie perhaps labels should be in their own directory by default?
                """
                pass
            # project.directory_default_id = project_directory_list[0].working_dir_id
            # session.add(project)
            else:
                log['error']["limit"] = "Can't archive default directory."
                return log

        directory.archived = True
        link.archived = True
        job_dir_sync_manager = job_dir_sync_utils.JobDirectorySyncManager(job=None,
                                                                          session=session,
                                                                          log=log,
                                                                          directory=directory)

        job_dir_sync_manager.remove_directory_from_all_attached_jobs()
        # Regenerate project dir cache.
        project.set_cache_key_dirty(cache_key="directory_list")

        return log
