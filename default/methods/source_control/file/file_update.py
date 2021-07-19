try:
    from methods.regular.regular_api import *
    from methods.source_control.file.remove import remove_core as file_remove_core
    from methods.source_control.file.file_browser import File_Browser

except:
    from default.methods.regular.regular_api import *
    from default.methods.source_control.file.remove import remove_core as file_remove_core
    from default.methods.source_control.file.file_browser import File_Browser

from shared.utils import job_dir_sync_utils
from shared.utils.sync_events_manager import SyncEventManager
from shared.utils.source_control.file.file_transfer_core import file_transfer_core
from shared.database.batch.batch import InputBatch
@routes.route('/api/v1/project/<string:project_string_id>' +
              '/file/update',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
@limiter.limit("300 per day")
def api_file_update(project_string_id):
    """
    For limits for this, this route may be used for single files (not just lists)

    """

    # TODO how do we want to handle this for labels?
    # I like enfocring a directory id with the request
    # But labels requires using fallback. (project default)

    spec_list = [{'file_list': list},
                 {'directory_id': None},
                 {'mode': str},
                 {'select_from_metadata': None},
                 {'cascade_archive_tasks': None},
                 {'metadata_proposed': None}]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        user = User.get(session=session)
        project = Project.get(session, project_string_id)

        source_directory = WorkingDir.get_with_fallback(
            session=session,
            directory_id=input['directory_id'],
            project=project)

        if source_directory is False:
            log['error']['directory'] = "No directory found"
            return jsonify(log=log), 400
        log = file_update_core(
            session=session,
            project=project,
            source_directory=source_directory,
            file_list=input['file_list'],
            mode=input['mode'],
            log=log,
            member=user.member,
            select_from_metadata=input['select_from_metadata'],
            cascade_archive_tasks=input['cascade_archive_tasks'],
            metadata_proposed=input['metadata_proposed']
        )

        if len(log["error"].keys()) >= 1:
            return jsonify(log=log), 400

        Event.new(
            session=session,
            kind="file_list_update",
            member_id=user.member_id,
            project_id=project.id,
            description=str(log['info'])
        )

        log['success'] = True
        return jsonify(log=log), 200


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/file/transfer',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
@limiter.limit("1000 per day")
def api_file_transfer(project_string_id):
    """
    This is a seperate route becuase we want to use spec_list
    properly. (even though in through it could be part of file update,
    and uses file_update_core).
    Not sure if this is a good pattern or not
    Benefit is gauranteed spec checking, plus record of a different
    URL end point logged for "free". Downside maybe is just more
    code, ie if changing core() then (may) need to update in more places.

    """

    spec_list = [
        {'file_list': list},
        {'destination_directory_id': int},
        {'source_directory_id': {
            'default': None,
            'kind': int,
            'required': False
        }
        },
        {'mode': {
            'default': 'TRANSFER',
            'valid_values_list': ['TRANSFER', 'REMOVE'],
            'kind': str,
            'required': False
        }
        },
        {'transfer_action': {
            'default': 'mirror',
            'valid_values_list': ['mirror', 'copy', 'move'],
            'kind': str,
            'required': False
        }
        },
        {'copy_instances': {
            'default': False,
            'kind': bool,
            'required': False
        }
        },
        {'select_from_metadata': None},
        {'metadata_proposed': None}
    ]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        source_directory = None

        if input['source_directory_id']:
            source_directory = WorkingDir.get_with_fallback(
                session=session,
                directory_id=input['source_directory_id'],
                project=project)

            if source_directory is False:
                log['error']['directory'] = "No directory found"
                return jsonify(log=log), 400

        member = get_member(session=session)

        log = file_update_core(
            session=session,
            project=project,
            source_directory=source_directory,
            file_list=input['file_list'],
            mode=input['mode'],
            transfer_action=input['transfer_action'],
            destination_directory_id=input['destination_directory_id'],
            copy_instances=input['copy_instances'],
            log=log,
            member=member,
            select_from_metadata=input['select_from_metadata'],
            metadata_proposed=input['metadata_proposed']
        )

        if len(log["error"].keys()) >= 1:
            return jsonify(log=log), 400

        Event.new(
            session=session,
            kind="file_list_transfer",
            member=member,
            project_id=project.id,
            description=str(log['info'])
        )

        log['success'] = True
        return jsonify(log=log), 200


def file_update_core(
        session,
        project,
        source_directory,
        file_list,
        mode,
        log,
        member,
        transfer_action=None,
        destination_directory_id=None,
        copy_instances=False,
        cascade_archive_tasks=False,
        select_from_metadata=False,
        metadata_proposed=None
):
    # TODO record member making these changes

    # TODO Handle status / results from remove_core better

    # TODO limits as a seperate function?
    # Some limits we want to do in advance so not
    # running for every file
    # (Where applicable, some checks could be per file.)

    # if transfer_action == "move":
    # do something

    if source_directory:
        if source_directory.id == destination_directory_id:
            if mode in ["mirror", "move"]:
                log['error']['transfer'] = "Already in directory, nothing to move."
                return log

    if select_from_metadata is True:

        metadata_proposed['start_index'] = 0
        metadata_proposed['limit'] = 2500

        file_browser_instance = File_Browser(
            session=session,
            project=project,
            directory=source_directory,
            metadata_proposed=metadata_proposed,
            member = member
        )

        file_list = file_browser_instance.file_view_core(
            mode="objects")

        log['metadata_proposed'] = metadata_proposed

        # Error case
        if not isinstance(file_list, list):
            # TODO some additional logging / output from file view?
            log['error']['metadata'] = "No files matched request"
            return log

    file_touched_count = 0
    batch = InputBatch.new(
        session = session,
        status = 'pending',
        project_id = project.id,
        member_created_id = member.id,
        memeber_updated_id = member.id
    )

    for file_dict in file_list:

        if select_from_metadata is not True:
            file_id = file_dict.get("id", None)
            if not file_id:
                log["error"]["Missing file id(s)"] = "One or more files are missing the id"
                continue

            file = File.get_by_id_and_project(
                session=session,
                project_id=project.id,
                file_id=file_id)

            if not file:
                log["error"][str(file_id)] = "Invalid ID for this project."
                continue

        if select_from_metadata is True:
            # Context that original setup assumed untrusted
            # But if select_from_metadata is True
            # then source of file list is trusted.
            file = file_dict

        file_touched_count += 1

        if mode == "REMOVE":
            # TODO handle if no source_directory
            result = file_remove_core(
                session=session,
                working_dir=source_directory,
                existing_file=file,
                cascade_archive_tasks = cascade_archive_tasks)

        if mode == "TRANSFER":

            destination_directory = WorkingDir.get(
                session=session,
                directory_id=destination_directory_id,
                project_id=project.id)

            if destination_directory is None:
                log['info']['transfer'] = "Invalid destination directory" + \
                                          " Check if the directory id is correct."
                return log

            log = file_transfer_core(
                session=session,
                source_directory=source_directory,
                destination_directory=destination_directory,
                transfer_action=transfer_action,
                copy_instances=copy_instances,
                file=file,
                log=log,
                member=member,
                defer_sync=True,
                defer_copy=True,
                batch_id = batch.id
            )

    if mode == "REMOVE":
        log['info']['remove'] = "Removed " + \
                                str(file_touched_count) + " file(s)."

    if mode == "TRANSFER":
        if transfer_action == "copy":
            log['info']['transfer_count'] = "Copied " + \
                                            str(file_touched_count) + " file(s)."

        if transfer_action == "move":
            log['info']['transfer_count'] = "Moved " + \
                                            str(file_touched_count) + " file(s)."

    # We could log this for all of these operations I guess
    # But seems especially important for the select from meta data
    # as we add that to the log
    # Caution at the moment it will show success as false due to placement
    # alternative is to have it twice...
    if select_from_metadata is True:
        Event.new(
            session=session,
            kind="bulk_file_operation",
            member=member,
            project_id=project.id,
            error_log=log
        )

    return log



