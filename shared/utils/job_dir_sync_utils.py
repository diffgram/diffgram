# OPENCORE - ADD
from shared.database.source_control.working_dir import WorkingDir, WorkingDirFileLink
from shared.database.task.task import Task
from shared.database.task.job.job import Job
from shared.database.source_control.file import File
from dataclasses import dataclass
from shared.utils.sync_events_manager import SyncEventManager
from shared.shared_logger import get_shared_logger
from shared.database.task.job.job_working_dir import JobWorkingDir
from shared.regular import regular_log

logger = get_shared_logger()


@dataclass
class JobDirectorySyncManager:
    session: any
    log: any
    job: any = None
    directory: any = None
    file: File = None  # WIP maybe more clear to do this, although there are cases with multiple files...

    def __add_file_into_job(
        self,
        file: File,
        incoming_directory: WorkingDir,
        job: Job = None,
        create_tasks: bool = False,
        sync_event_manager = None):
        """
            Given a file, add the link to the job directory and create a task if create_tasks=True.
        :param session:
        :param file:
        :param dir:
        :param job:
        :param log:
        :param create_tasks:
        :return:
        """

        job_obj = self.job
        if job is not None:
            job_obj = job

        result, log = WorkingDirFileLink.file_link_update(
            session = self.session,
            add_or_remove = 'add',
            incoming_directory = incoming_directory,
            directory = job_obj.directory,
            file_id = file.id,
            job = job_obj,
            log = self.log
        )
        logger.debug(f"File {file.id} added to job {job_obj.id}")

        if create_tasks is False:
            log['info']['create_tasks flag'] = "create_tasks is False"
            return True, log

        valid_status_to_create_tasks = ['active', 'in_review', 'complete']
        if job_obj.status not in valid_status_to_create_tasks:
            log['info']['job status'] = f"not in {str(valid_status_to_create_tasks)}"
            logger.debug(
                f"Job status not active, skipping. Statuses must be one of {str(valid_status_to_create_tasks)}")
            return True, log

        logger.debug('Creating task...')
        potential_existing_task = self.__check_if_task_exists(
            job = job_obj,
            file = file)
        if potential_existing_task is None:
            task = self.create_task_from_file(file, job = job_obj, incoming_directory = incoming_directory)
            task.is_root = True
            logger.debug(f"New task created. {task.id}")
        else:
            task = potential_existing_task

        if sync_event_manager:
            sync_event_manager.add_create_task(task)
            sync_event_manager.set_status('completed')
        if result is not True:
            log['error']['create_file_links'] = f"Error creating links for file id: {file.id}"
            return False, log
        if regular_log.log_has_error(log):
            return False, log

        return True, log

    def __check_if_task_exists(
        self,
        job: Job,
        file: File):
        task = Task.get_by_job_and_file(
            session = self.session,
            job = job,
            file = file)
        if task:
            logger.debug('Task already exists.')
        return task

    def __sync_all_jobs_from_dir(
        self,
        file: File,
        file_link_dir: WorkingDir,
        directory_for_job_sync: WorkingDir,
        create_tasks = False,
        member = None):
        """
            Inner function. Gets all job ids from the directory given in the param directory_for_job_sync
            and calls function for creating a new task on each job with the given file.
        :param file: The file to create a task from.
        :param file_link_dir: The directory where the file is (The source directory if a file is being moved)
        :param directory_for_job_sync: The directory to get the jobs from.
        :param create_tasks: create task for the given file, if not True only file link will be created to the job dir.
        :return:
        """

        if not directory_for_job_sync:
            self.log['error']['directory_for_job_sync'] = "Missing directory_for_job_sync"
            logger.error('Missing directory_for_job_sync')
            return False, self.log

        job_list = JobWorkingDir.list(
            session = self.session,
            class_to_return = Job,
            working_dir_id = directory_for_job_sync.id,
            sync_type = 'sync'
        )
        for job in job_list:
            sync_event_manager = SyncEventManager.create_sync_event_and_manager(
                session = self.session,
                dataset_source_id = directory_for_job_sync,
                dataset_destination = None,
                description = 'Sync file from dataset {} to job {} and create task'.format(
                    directory_for_job_sync.nickname,
                    job.name
                ),
                file = file,
                job = job,
                input_id = file.input_id,
                project = job.project,
                event_effect_type = 'create_task',
                event_trigger_type = 'file_added',
                status = 'init',
                member_created = member
            )

            self.__add_file_into_job(
                file,
                file_link_dir,
                job = job,
                create_tasks = create_tasks,
                sync_event_manager = sync_event_manager)

            if regular_log.log_has_error(self.log):
                return False, self.log
            job.update_file_count_statistic(session = self.session)
        return True, self.log

    def remove_directory_from_all_attached_jobs(self, soft_delete = True):
        """
            Removes the given directory (self.directory) from all the jobs it is attached to that are in 'sync' mode.
        :return:
        """
        if self.directory is None:
            self.log['error']['directory'] = 'Please provide directory object to the JobDirectorySyncManager'
            return False, self.log

        if soft_delete:
            self.session.query(JobWorkingDir).filter(JobWorkingDir.working_dir_id == self.directory.id)
        else:
            self.session.query(JobWorkingDir).filter(JobWorkingDir.working_dir_id == self.directory.id).update(
                {"sync_type": "archived"}
            )
        logger.info(f"Removed  {self.directory.id} from jobs.")
        self.log['info'][f"working_dir_updates_{self.directory.id}"] = f"Removed  {self.directory.id} from jobs."
        return True, self.log

    def remove_job_from_all_dirs(self, soft_delete = True):
        """
            Removes the job from all the directories it had been attached by clearing all
            the JobWorking dirs relations with the given job ID.
        :return:
        """

        if self.job is None:
            self.log['error']['job'] = 'Please provide job object to the JobDirectorySyncManager'
            return False, self.log
        # Delete relation of  directories from job.
        if not soft_delete:
            self.session.query(JobWorkingDir).filter(JobWorkingDir.job_id == self.job.id).delete()
        else:
            self.session.query(JobWorkingDir).filter(JobWorkingDir.job_id == self.job.id).update(
                {"sync_type": "archived"}
            )
        return True, self.log

    def create_task_from_file(self, file, job = None, incoming_directory = None):

        job_obj = self.job
        if job is not None:
            logger.debug(f"Creating task from file {file.id} and job {job.id}")
            job_obj = job
        if job_obj.file_handling == "isolate":
            new_file = File.copy_file_from_existing(
                session = self.session,
                working_dir = job_obj.directory,
                existing_file = file,
                copy_instance_list = False,
                add_link = False,
                remove_link = False,
                orginal_directory_id = job_obj.completion_directory_id,
                deep_copy = True,
                ann_is_complete_reset = True
            )
        else:  # assume use existing
            new_file = file
            new_file.ann_is_complete = False
            self.session.add(new_file)
        task = Task.new(
            self.session,
            job_obj,
            new_file.id,
            job_obj.guide_default_id,
            job_obj.label_dict,
            file_original_id = file.id,
            kind = 'human',
            task_type = 'draw',
            incoming_directory = incoming_directory
        )
        # Set job as not completed.
        job_obj.status = 'active'
        self.session.add(job_obj)
        self.session.add(task)
        return task

    def add_file_to_all_jobs(self, file, source_dir = None, create_tasks = False, member = None):
        """
            Adds file to all the attached jobs on the managed directory (self.directory). An optional source_dir
            parameter is provided in case the file is being moved or copied from another directory and the file link
            has not been committed to DB yet. On this case, the function will use the source_dir instead of
            self.directory for the file_link validation, but it will still search for the jobs on self.directory.
        :param file:
        :param source_dir:
        :param create_tasks:
        :return:
        """
        logger.debug(f"Add files to all jobs file:{file.id} create tasks: {create_tasks}")
        file_link_directory = self.directory
        if source_dir:
            file_link_directory = source_dir

        self.__sync_all_jobs_from_dir(
            file = file,
            file_link_dir = file_link_directory,
            directory_for_job_sync = self.directory,
            create_tasks = create_tasks,
            member = member
        )

    def create_file_links_for_attached_dirs(self,
                                            sync_only = False,
                                            create_tasks = False,
                                            file_to_link = None,
                                            file_to_link_dataset = None,
                                            related_input = None,
                                            member = None):
        """
            Called once before launch. This function will check all directories
            in JobWorkingDir table
            and create the file links for all the related files. This function
            will create links for both "sync" type and "select". "select" type dirs
            will just be linked once (ie new files added to dir wont be updated),
            sync types dirs will update links on process_media when a new file is attached to the dir
            or when a file is copied or moved to the sync directory.
        :param session:
        :param job:
        :param log:
        :return:

        """

        # Now create a file link for all the files on all the directories on the job and attach them.
        if sync_only:
            directory_list = self.job.get_attached_dirs(session = self.session)

        else:
            directory_list = self.job.get_attached_dirs(session = self.session, sync_types = ['sync', 'select_once'])
        if len(directory_list) == 0:
            self.log['info']['attached_directories_list'] = 'No directories attached.'
            return directory_list
        if file_to_link is None or file_to_link_dataset is None:
            # Case where we do not provide a single file for sync (i.e no file_to_link or file_to_link_dataset)
            for directory in directory_list:
                if self.job.instance_type in ['text_tokens']:
                    files = WorkingDirFileLink.file_list(
                        self.session,
                        working_dir_id = directory.id,
                        root_files_only = True,  # TODO do we need to get child files too?
                        limit = None,
                        type = 'text'
                    )
                else:
                    files = WorkingDirFileLink.file_list(
                        self.session,
                        working_dir_id = directory.id,
                        root_files_only = True,  # TODO do we need to get child files too?
                        limit = None,
                    )
                for file in files:
                    logger.debug('Single file sync event with file: {} and folder {}'.format(
                        directory,
                        file))
                    sync_event_manager = SyncEventManager.create_sync_event_and_manager(
                        session = self.session,
                        dataset_source_id = directory.id,
                        dataset_destination = None,
                        description = 'Sync file {} from dataset {} to job {} and create task'.format(
                            file.original_filename,
                            directory.nickname,
                            self.job.name
                        ),
                        file = file,
                        job = self.job,
                        input = related_input,
                        project = self.job.project,
                        event_effect_type = 'create_task',
                        event_trigger_type = 'file_added',
                        status = 'init',
                        member_created = member
                    )
                    logger.debug(f"Created sync_event {sync_event_manager.sync_event.id}")
                    result, log = self.__add_file_into_job(
                        file,
                        directory,
                        create_tasks = create_tasks,
                        sync_event_manager = sync_event_manager
                    )
                    if result is not True:
                        log['error']['sync_file_dirs'] = f"Error syncing dirs for file id: {file.id}"
                    if regular_log.log_has_error(log):
                        return False, log
        else:
            logger.debug(
                f"Single file sync event with file: {file_to_link_dataset.id} and folder {file_to_link.id}")
            sync_event_manager = SyncEventManager.create_sync_event_and_manager(
                session = self.session,
                dataset_source_id = file_to_link_dataset.id,
                dataset_destination = None,
                description = 'Sync file {} from dataset {} to job {} and create task'.format(
                    file_to_link.original_filename,
                    file_to_link_dataset.nickname,
                    self.job.name
                ),
                file = file_to_link,
                job = self.job,
                input = related_input,
                project = self.job.project,
                event_effect_type = 'create_task',
                event_trigger_type = 'file_added',
                status = 'init',
                member_created = member
            )
            logger.debug(f"Created sync_event {sync_event_manager.sync_event.id}")
            result, log = self.__add_file_into_job(
                file_to_link,
                file_to_link_dataset,
                create_tasks = create_tasks,
                sync_event_manager = sync_event_manager,
            )
            if result is not True:
                log['error']['sync_file_dirs'] = f"Error syncing dirs for file id: {file_to_link.id}"
            if regular_log.log_has_error(log):
                return False, log
        self.job.update_file_count_statistic(session = self.session)
        return True, self.log
