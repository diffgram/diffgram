# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.source_control.working_dir import WorkingDir, WorkingDirFileLink
from shared.database.source_control.project_directory_list import ProjectDirectoryList, link as Project_Directory_List_link
from shared.utils import job_dir_sync_utils
from shared.database.source_control.project import Project

@routes.route('/api/v1/project/<string:project_string_id>' + '/directory/update', methods=['POST'])
@Project_permissions.user_has_project(Roles=["admin", "Editor"], apis_user_list=['api_enabled_builder', 'security_email_verified'])
@limiter.limit("100 per day")
def update_directory_api(project_string_id):
    """
    Updates a directory in the given project.
    """
    spec_list = [
        {"nickname": None},
        {"directory_id": int},
        {"mode": str}
    ]

    log, input, _ = regular_input.master(request=request, spec_list=spec_list)
    if log["error"]:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        project = Project.get(session, project_string_id)

        if not project:
            log["error"] = "Project not found"
            return jsonify(log=log), 400

        log = update_directory_core(
            session=session,
            project=project,
            nickname=input.get("nickname"),
            mode=input["mode"],
            directory_id=input["directory_id"],
            log=log
        )

        if log["error"]:
            return jsonify(log=log), 400

        log["success"] = True
        return jsonify(log=log), 200

def update_directory_core(session, project, nickname, mode, directory_id, log) -> dict:
    """
    Updates a directory based on the given mode.

    :param session: The database session.
    :param project: The project to update the directory in.
    :param nickname: The new nickname for the directory.
    :param mode: The mode to update the directory in.
    :param directory_id: The ID of the directory to update.
    :param log: The log dictionary to update with messages.
    :return: The updated log dictionary.
    """
    directory = WorkingDir.get(session=session, directory_id=directory_id, project_id=project.id)

    if not directory:
        log["error"] = "Directory not found"
        return log

    session.add(directory)

    link = Project_Directory_List_link(
        session=session,
        working_dir_id=directory.id,
        project_id=project.id
    )

    session.add(link)

    if mode == "RENAME":
        if not nickname:
            log["error"] = "No nickname provided"
            return log

        directory.nickname = nickname
        link.nickname = nickname
        log["info"] = "Updated Nickname."
        project.set_cache_key_dirty(cache_key="directory_list")

    elif mode == "ARCHIVE":
        if directory.id == project.directory_default_id:
            project_directory_list = ProjectDirectoryList.get_by_project(
                session=session,
                project_id=project.id,
                kind="objects",
                exclude_archived=True,
                directory_ids_to_ignore_list=[directory.id]
            )

            if not project_directory_list:
                log["error"]["limit"] = "Can't archive default directory."
                return log

            # Uncomment the following lines to allow archiving the default directory
            # project.directory_default_id = project_directory_list[0].working_dir_id
            # session.add(project)

        directory.archived = True
        link.archived = True
        job_dir_sync_manager = job_dir_sync_utils.JobDirectorySyncManager(job=None, session=session, log=log, directory=directory)
        job_dir_sync_manager.remove_directory_from_all_attached_jobs()
        project.set_cache_key_dirty(cache_key="directory_list")

    return log
