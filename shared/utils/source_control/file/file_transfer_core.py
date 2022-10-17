# OPENCORE - ADD
from shared.database.source_control.file import File
from shared.database.source_control.working_dir import WorkingDirFileLink, WorkingDir
from shared.utils.sync_events_manager import SyncEventManager
from shared.utils import job_dir_sync_utils
from shared.shared_logger import get_shared_logger
from shared.database.sync_events.sync_action_queue import SyncActionsQueue
from shared.database.auth.member import Member
from sqlalchemy.orm.session import Session

logger = get_shared_logger()


def perform_sync_events_after_file_transfer(session: Session,
                                            source_directory: WorkingDir,
                                            destination_directory: WorkingDir,
                                            log: dict,
                                            log_sync_events: bool,
                                            transfer_action: str,
                                            file: File,
                                            member: Member,
                                            new_file: File,
                                            defer_sync: bool,
                                            sync_event_manager: SyncEventManager = None):
    """
        This function is executed after a move/copy of a file. It logs the sync event and calls all the
        task templates that are observing the destination directory of the copy/move for creating tasks.
    :param session:
    :param source_directory:
    :param destination_directory:
    :param log:
    :param log_sync_events:
    :param transfer_action:
    :param file:
    :param member:
    :param new_file:
    :param defer_sync:
    :param sync_event_manager:
    :return:
    """
    if sync_event_manager is None and log_sync_events:
        sync_event_manager = SyncEventManager.create_sync_event_and_manager(
            session = session,
            dataset_source = source_directory,
            dataset_destination = destination_directory,
            description = 'File {} from dataset {} to dataset {}.'.format(
                transfer_action,
                source_directory.nickname if source_directory else '--',
                destination_directory.nickname,
            ),
            file = file,
            new_file_copy = new_file,
            job = None,
            input_id = file.input_id,
            project = file.project,
            created_task = None,
            completed_task = None,
            transfer_action = transfer_action,
            event_effect_type = f"file_{transfer_action}",
            event_trigger_type = 'file_operation',
            status = 'completed',
            member_created = member
        )
        logger.debug(f"Created sync_event {sync_event_manager.sync_event.id}")
    # TODO: UPDATE JOBS WHERE DIRECTORY SHOULD BE SYNCED
    # Note that at this point we pass the source directory even though new file link has been created.
    # This is because the session has not been committed and new file link still won't be found in query.
    if not defer_sync:
        job_dir_sync_manager = job_dir_sync_utils.JobDirectorySyncManager(
            session = session,
            log = log,
            directory = destination_directory,
        )
        # Note we add the source directory here, because file link has not been committed. So the file link
        # on destination directory still does not exist at this point. That's why we need to provide the source
        # dir, so validation of incoming directory does not fail when checking the directory the file is coming from.
        job_dir_sync_manager.add_file_to_all_jobs(
            file = file,
            source_dir = source_directory,
            create_tasks = True,

        )
    else:
        if log_sync_events and sync_event_manager.sync_event.event_trigger_type == 'file_operation':
            SyncActionsQueue.enqueue(session, sync_event_manager.sync_event)


def transfer_child_files(session,
                         source_directory: WorkingDir,
                         destination_directory: WorkingDir,
                         transfer_action: str,
                         compound_file: File,
                         log: dict,
                         member: Member = None,
                         copy_instances: bool = False,
                         sync_event_manager: SyncEventManager = None,
                         log_sync_events: bool = True,
                         defer_sync: bool = False,
                         defer_copy: bool = True,
                         batch_id: int = None,
                         new_parent_id: int = None,
                         update_project_for_copy: bool = False):
    if compound_file.type != 'compound':
        return
    child_files = compound_file.get_child_files(session = session)
    for child in child_files:
        file_transfer_core(
            session = session,
            source_directory = source_directory,
            destination_directory = destination_directory,
            transfer_action = transfer_action,
            log = log,
            member = member,
            file = child,
            copy_instances = copy_instances,
            sync_event_manager = sync_event_manager,
            log_sync_events = log_sync_events,
            defer_sync = defer_sync,
            defer_copy = defer_copy,
            batch_id = batch_id,
            update_project_for_copy = update_project_for_copy,
            new_parent_id = new_parent_id
        )


def file_transfer_core(
    session: Session,
    source_directory: WorkingDir,
    destination_directory: WorkingDir,
    transfer_action: str,
    file: File,
    log: dict,
    member: Member = None,
    copy_instances: bool = False,
    sync_event_manager: SyncEventManager = None,
    log_sync_events: bool = True,
    defer_sync: bool = False,
    defer_copy: bool = True,
    batch_id: int = None,
    new_parent_id: int = None,
    update_project_for_copy = False,
):
    """

    source_directory and destination_directory are trusted, assumed to be valid here

    copy_instances, bool

    """
    new_file = None
    if transfer_action == "copy":
        new_file = File.copy_file_from_existing(
            session = session,
            working_dir = destination_directory,
            orginal_directory_id = source_directory.id if source_directory else None,
            existing_file = file,
            copy_instance_list = copy_instances,
            log = log,
            add_link = True,
            remove_link = False,
            flush_session = True,
            defer_copy = defer_copy,
            batch_id = batch_id,
            new_parent_id = new_parent_id
        )
        session.flush()
        if defer_copy:
            return log
        perform_sync_events_after_file_transfer(session = session,
                                                source_directory = source_directory,
                                                destination_directory = destination_directory,
                                                log = log,
                                                log_sync_events = log_sync_events,
                                                transfer_action = transfer_action,
                                                file = file,
                                                member = member,
                                                new_file = new_file,
                                                defer_sync = defer_sync,
                                                sync_event_manager = None)

        if not log['info'].get('new_file', []):
            if new_file:
                log['info']['new_file'] = [new_file.serialize_with_type(session)]
        else:
            if new_file:
                log['info']['new_file'].append(new_file.serialize_with_type(session))
        if not log['info'].get('message'):
            log['info']['message'] = 'File Copy Success.'

    if transfer_action == "move":
        # Get existing link
        link = WorkingDirFileLink.file_link(
            session = session,
            working_dir_id = source_directory.id,
            file_id = file.id)
        if link is None:
            log["error"]['file_link'] = 'File link of file: {} and workingdir: {}. Does not exists'.format(
                source_directory.id,
                file.id
            )

        # TODO consider how this effects committed
        # Is it safe to just "update" it this way?
        # SHould this be a built in method of WorkingDirFileLink
        new_link = WorkingDirFileLink.file_link(
            session = session,
            working_dir_id = destination_directory.id,
            file_id = file.id)
        if new_link is not None:
            log["error"]['file_link'] = 'File link of file: {} and Destination workingdir: {}. Already Exists'.format(
                source_directory.id,
                file.id
            )
            return log
        link.working_dir_id = destination_directory.id
        session.add(link)

        perform_sync_events_after_file_transfer(
            session = session,
            source_directory = source_directory,
            destination_directory = destination_directory,
            log = log,
            log_sync_events = log_sync_events,
            transfer_action = transfer_action,
            file = file,
            member = member,
            new_file = None,
            defer_sync = defer_sync,
            sync_event_manager = sync_event_manager
        )

    if transfer_action == "mirror":

        existing_link = WorkingDirFileLink.file_link(
            session = session,
            working_dir_id = destination_directory.id,
            file_id = file.id
        )

        if existing_link is not None:
            log["error"][str(file.id)] = "File already in dataset id: " + \
                                         str(destination_directory.id)
            return log

        link = WorkingDirFileLink.add(
            session = session,
            working_dir_id = destination_directory.id,
            file = file)
        log["info"][str(file.id)] = True

    # If file is compound, transfer all child files too.
    if file.type == 'compound':
        transfer_child_files(
            session = session,
            source_directory = source_directory,
            destination_directory = destination_directory,
            transfer_action = transfer_action,
            compound_file = file,
            log = log,
            member = member,
            copy_instances = copy_instances,
            sync_event_manager = sync_event_manager,
            log_sync_events = log_sync_events,
            defer_sync = defer_sync,
            defer_copy = defer_copy,
            batch_id = batch_id,
            update_project_for_copy = update_project_for_copy,
            new_parent_id = new_file.id if new_file is not None else None)

    return log
