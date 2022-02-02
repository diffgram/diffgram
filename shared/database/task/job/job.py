from shared.database.common import *
from shared.database.task.task import Task
from shared.database.task.job.user_to_job import User_To_Job
from shared.database.source_control.working_dir import WorkingDirFileLink, WorkingDir
from shared.database.external.external import ExternalMap
from shared.database.task.job.job_working_dir import JobWorkingDir
from shared.database.source_control.file import File
from shared.database.user import User
from shared.database.event.event import Event
from shared.regular.regular_member import get_member
from shared.shared_logger import get_shared_logger
from shared.database.task.exam.exam import Exam

logger = get_shared_logger()

class Job(Base, Caching):
    """
    A job has many tasks.

    This object is now referred as Task Template in the UI, we still need to change variable name and table names
    but for now think about using Job/TaskTemplate interchangeably inside the code and try to refactor naming
    whenever possible.

    ***

    add stuff to copy_job_for_exam() if adding things!

    ***

    """

    __tablename__ = 'job'
    id = Column(Integer, primary_key=True)
    hidden = Column(Boolean, default=False)  # hidden or deleted...

    is_live = Column(Boolean, default=True)

    attached_directories_dict = Column(MutableDict.as_mutable(JSONEncodedDict),
                                       default={'attached_directories_list': []})


    security_require_email_verified = Column(Boolean, default=True)

    status = Column(String(), default="draft")
    # created (or draft?), active, in_review, reported, removed
    # save_for_later, complete, failed
    # in_progress vs "available" depends on point of reference

    type = Column(String(), default='Normal')  # ['Normal', 'Exam', 'Learning']

    is_template = Column(Boolean, default=False)
    # While we could intuit this from the exam id prefer explicit
    # If it's not a template then we assume it's an Instance of the Exam
    # (or could apply to other template / instance things in future.)

    is_pinned = Column(Boolean(), default = False)

    instance_type = Column(String)
    # ['polygon', 'box', 'tag', 'text_tokens']

    pro_network = Column(Boolean, default=False)        # Prior had "market" as a share type but a single bool here is more clear.

    
    default_userscript_id = Column(Integer, ForeignKey('userscript.id'))
    default_userscript = relationship("UserScript", foreign_keys=[default_userscript_id])

    share_type = Column(String())  # ['Market', 'project', 'org']
    permission = Column(String())  # ['invite_only', 'Only me', 'all_secure_users']

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project")

    category = Column(String(), default='visual')

    guide_default_id = Column(Integer, ForeignKey('guide.id'))
    guide_default = relationship("Guide", foreign_keys=[guide_default_id])

    guide_review_id = Column(Integer, ForeignKey('guide.id'))
    guide_review = relationship("Guide", foreign_keys=[guide_review_id])


    ui_schema_id = Column(Integer, ForeignKey('ui_schema.id'))
    ui_schema = relationship("UI_Schema", foreign_keys=[ui_schema_id])

    # Primary data storage for job
    directory_id = Column(Integer, ForeignKey('working_dir.id'))
    directory = relationship("WorkingDir",
                             foreign_keys=[directory_id])

    # Question, is this also the "original" direction? needed for case of video where original directory
    # is not clear. (video link gets added as normal, but then the video's associated files are seperate right.)
    completion_directory_id = Column(Integer, ForeignKey('working_dir.id'))
    completion_directory = relationship("WorkingDir",
                                        foreign_keys=[completion_directory_id])

    interface_connection_id = Column(Integer, ForeignKey('connection_base.id'))
    interface_connection = relationship("Connection",
                                        foreign_keys=[interface_connection_id])

    completion_action = Column(String())

    exam_id = Column(Integer, ForeignKey('exam.id'))  # New Feb 8, 2019
    exam = relationship("Exam")

    # Review settings
    # can't seem to make up mind on "file" vs "pass"
    review_by_human_freqeuncy = Column(String(), default="every_3rd_pass")
    allow_reviews = Column(Boolean(), default=False)
    # ['every_pass', 'every_3rd_pass', 'every_10th_pass', 'none']

    # Label  / quality settings

    # open == Support for trainers adding their own labels
    # closed == trainers can't change it
    label_mode = Column(String)
    # 'closed_and_split_one_label_per_task', 
    # 'closed_all_available', 'open'  
    # Cached in task

    passes_per_file = Column(Integer)  # 1, 3, ...

    send_tasks_to_external_provider_on_launch = Column(Boolean, default=False)

    file_count = Column(Integer)  # user declared
    launch_datetime_deferred = Column(DateTime)  # system set, ie
    # a rate limit on number of attempts
    launch_datetime = Column(DateTime)  # original / user set
    launch_attempt_log = Column(MutableDict.as_mutable(JSONEncodedDict),
                                default={})
    waiting_to_be_launched = Column(Boolean, default=False)

    pending_initial_dir_sync = Column(Boolean, default=False)

    # Available / selected label files
    # By default all on project? # Do we really need this or just get by project?
    # I guess if it changes would be good to have it here.

    # Cache this in task too ?
    # BUT may be different depending on the mode
    label_dict = Column(MutableDict.as_mutable(JSONEncodedDict),
                        default={'label_file_list_serialized': [],
                                 'label_file_colour_map': {}})

    # We are controlling delete behaviour manually in job_cancel.job_cancel_core()
    # Could use delete cascade instead?

    # We don't have a task_list using sql alchemy relationships
    # ie { task_list = relationship("Task") }
    # Here since we define it as a function below
    # And it creates confusion / strange errors to have both!
    # We could have both and name differently but not clear when it would be needed...

    review_chance = Column(Float, default = 1.0)

    name = Column(String())
    description = Column(String())

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys=[member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys=[member_updated_id])

    time_created = Column(DateTime, default=datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)
    time_completed = Column(DateTime)

    # Credential requirements??

    # ie defualts like / static requirements
    # requires_user_verified
    # requires_passed_xyz...

    # dynamic requirements like
    # "Credential xyz"  (credential to job thing here maybe?)

    # Stats
    stat_last_updated_time = Column(Integer)

    file_count_statistic = Column(Integer)

    # Question, if there are changes to a job
    # Do we update the stats? some assumptions for say complting are
    # based on this...
    stat_count_tasks = Column(Integer)

    # Question do we want to set this to 0 ie
    # in case it shows up on details page or some other error...
    # Setting default of 0 doesn't fix this automatically though
    # 0 / 0 is undefined still
    stat_count_complete = Column(Integer, default=0)
    stat_count_labels = Column(Integer)

    ##### GRAPH

    is_root = Column(Boolean)
    root_id = Column(Integer, ForeignKey('job.id'))

    parent_id = Column(Integer, ForeignKey('job.id'))
    parent = relationship("Job",
                          uselist=False,
                          foreign_keys=[parent_id])

    repeatable = Column(Boolean)  # True for exam? Do we actually need this here?
    # repeatable limit?

    file_handling = Column(String)  # [None, "use_existing", "isolate"]

    output_dir_action = Column(String)  # ['copy', 'move', 'nothing']

    # External ID's for referencing on integrations like Labelbox, Supervisely, etc.
    default_external_map_id = Column(BIGINT, ForeignKey('external_map.id'))
    default_external_map = relationship("ExternalMap",
                                        uselist=False,
                                        foreign_keys=[default_external_map_id])

    cache_dict = Column(MutableDict.as_mutable(JSONEncodedDict), default={})

    #####

    def examination_exists(self, session, user):
        child_examinations = session.query(Job).filter(
            Job.parent_id == self.id,
            Job.type == 'examination',
            Job.status != 'archived'
        )
        child_id_list = [x.id for x in child_examinations]
        relations = session.query(User_To_Job).filter(
            User_To_Job.job_id.in_(child_id_list),
            User_To_Job.user_id == user.id
        ).all()
        if len(relations) > 0:
            return True
        return False


    def update_attached_directories(self, session, attached_directories_list, delete_existing=False):
        if attached_directories_list:
            # Delete existing directories
            if delete_existing:
                session.query(JobWorkingDir).filter(JobWorkingDir.job_id == self.id).delete()
            # Create new relations
            for directory in attached_directories_list:
                relation = JobWorkingDir(
                    job=self,
                    working_dir_id=directory['directory_id'],
                    sync_type=directory['selected']
                )
                session.add(relation)

    def get_attached_files(self, session, type=None, return_kind='all'):
        """

        :param session:
        :param type:
        :param return_kind: andy of 'all', 'first', 'count'
        :return:
        """
        if return_kind not in ['all', 'first', 'count']:
            return None
        dir_attachments = session.query(JobWorkingDir).filter(JobWorkingDir.job_id == self.id).all()
        dir_ids = [dir.working_dir_id for dir in dir_attachments]
        if type:
            files_to_process = session.query(File).join(WorkingDirFileLink).filter(
                WorkingDirFileLink.working_dir_id.in_(dir_ids),
                File.type == type,
                File.state != 'removed'
            )
        else:
            files_to_process = session.query(File).join(WorkingDirFileLink).filter(
                WorkingDirFileLink.working_dir_id.in_(dir_ids),
                File.state != 'removed'
            )
        if return_kind == 'all':
            return files_to_process.all()
        elif return_kind == 'count':
            return files_to_process.count()
        elif return_kind == 'first':
            return files_to_process.first()

    def get_by_id(session, job_id):
        if job_id is None:
            return None

        return session.query(Job).filter(
            Job.id == job_id).first()

    def get_label_file_by_name(self, name):
        if not self.label_dict or not self.label_dict.get('label_file_list_serialized'):
            return
        for label_element in self.label_dict['label_file_list_serialized']:
            if label_element['label']['name'] == name:
                return label_element
        return None

    def get_attribute_group_by_name(self, label_file_dict, name):
        if not self.label_dict or not self.label_dict.get('label_file_list_serialized'):
            return
        for attribute_group in label_file_dict['attribute_group_list']:
            if attribute_group['name'] == name:
                return attribute_group

        return None

    def get_attribute_template_by_name(self, attr_group, name):

        if not self.label_dict or not self.label_dict.get('label_file_list_serialized'):
            return
        for attribute_template in attr_group['attribute_template_list']:
            if attribute_template['name'] == name:
                return attribute_template
        return None

    def get_reviewers(self, session):
        rels = User_To_Job.list(session = session, job = self, relation = 'reviewer')
        users = [rel.user for rel in rels]
        return users

    def get_assignees(self, session):
        rels = User_To_Job.list(session = session, job = self, relation = 'annotator')
        users = [rel.user for rel in rels]
        print([x.job_id for x in rels])
        print('GET ASSIGNEES', users)
        return users


    def check_existing_user_relationship(
            self,
            session,
            user_id: int):

        existing_user_to_job = User_To_Job.get_single_by_ids(
            session=session,
            user_id=user_id,
            job_id=self.id)

        if self.repeatable is not True:
            if existing_user_to_job:
                return True

        if self.repeatable is True:
            # Even if the job can be repeated (ie an exam),
            # We don't want two of the same jobs happening at once
            if existing_user_to_job.status in ['active', 'pending']:
                return True

        return False


    def get_jobs_open_to_all(
            session,
            project):

        query = session.query(Job)
        
        query = query.filter(Job.project_id == project.id)

        query = query.filter(
            or_(
                Job.permission == 'all_secure_users', 
                Job.permission == None))

        return query.all()



    def get_job_IDS_open_to_all(
            session,
            project):

        ids_list = []
        valid_jobs_open_to_all = Job.get_jobs_open_to_all(
            session = session,
            project = project)
        if not valid_jobs_open_to_all:
            return ids_list

        for job in valid_jobs_open_to_all:
            ids_list.append(job.id)
        return ids_list



    def attach_user_to_job(
            self,
            session,
            user,
            add_to_session: bool = False,
            relation: str = 'annotator'):

        user_to_job = User_To_Job(
            job = self,
            user = user,
            relation = relation)

        if add_to_session:
            session.add(user_to_job)

        return user_to_job

    def remove_user_from_job(
            session,
            user_to_job,
            add_to_session: bool = False):

        user_to_job.archived = True
        session.add(user_to_job)

    def update_reviewer_list(self, session: 'Session', reviewer_list_ids: list, log: dict):
        """
            Updates the reviewer list of the job to the list provided in
            reviewer_list_ids. All other members not in the list will be removed as reviewers
            from the job.
        :param session:
        :param reviewer_list_ids:
        :param log:
        :return:
        """
        if reviewer_list_ids is None:
            data_str = 'reviewer_list_ids must not be None, skipping update_reviewer_list()'
            logger.warning(data_str)
            log['info']['reviewer_list_ids'] = data_str
            return log
        user_list = []
        log['info']['reviewer_list'] = {}

        # Populate User List
        if 'all' in reviewer_list_ids:
            user_list = self.project.users
        else:
            for member_id in reviewer_list_ids:

                user = User.get_by_member_id(
                    session=session,
                    member_id=member_id)
                if not user:
                    log['error']['reviewer_list'] = {}
                    log['error']['reviewer_list'][member_id] = "Invalid member_id " + str(member_id)
                    return log
                else:
                    user_list.append(user)

        # Now create user_to_job relations.
        user_added_id_list = []
        for user in user_list:

            user_added_id_list.append(user.id)

            existing_user_to_job = User_To_Job.get_single_by_ids(
                session=session,
                user_id=user.id,
                job_id=self.id,
                relation = 'reviewer'
            )

            if existing_user_to_job:
                # Add user back into job
                if existing_user_to_job.status == 'removed':
                    existing_user_to_job.status = 'active'
                    log['info']['reviewer_list'][user.member_id] = "Added"
                    session.add(existing_user_to_job)
                else:
                    log['info']['reviewer_list'][user.member_id] = "Unchanged."
                continue

            self.attach_user_to_job(
                session=session,
                user=user,
                add_to_session=True,
                relation = 'reviewer'
            )

            log['info']['reviewer_list'][user.member_id] = "Added"

        # Marked all relations not provided as removed.
        remaining_user_to_job_list = User_To_Job.list(
            session=session,
            user_id_ignore_list=user_added_id_list,
            relation = 'reviewer'
        )

        for user_to_job in remaining_user_to_job_list:
            if user_to_job.status != 'removed':
                user_to_job.status = 'removed'
                session.add(user_to_job)
                # TODO this should be uniform, it's not right now
                # this is update_user_list but we need to add member_id to user_to_job
                # it sounds like this needed to be member_list for current tests so just leaving it for now.
                log['info']['reviewer_list'][user_to_job.user_id] = "Removed"

        self.set_cache_by_key(
            cache_key='reviewer_list_ids',
            value=reviewer_list_ids)
        session.add(self)
        return log

    def update_member_list(
            self,
            member_list_ids: list,
            session,
            log: dict,
            add_to_session: bool = True):

        # TODO feel like this could be a more generic pattern
        # main id is given a list of ids handle updating the attachments
        # TODO abstract more functions here...

        # TODO optimize by caching
        # / checking existing_member_list_ids

        # An empty list is OK because that indicates clearing all 
        if member_list_ids is None:
            log['info']['member_list_ids'] = 'Provide member lists IDs'
            return log

        log['info']['update_user_list'] = {}
        log['info']['update_member_list'] = {}

        user_list = []
        user_added_id_list = []
        print('member_list_ids', member_list_ids)
        if 'all' in member_list_ids:
            user_list = self.project.users
            self.permission = "all_secure_users"
            session.add(self)

        else:
            self.permission = "invite_only"
            session.add(self)
            for member_id in member_list_ids:

                user = User.get_by_member_id(
                    session=session,
                    member_id=member_id)

                if not user:
                    log['error']['update_member_list'] = {}
                    log['error']['update_member_list'][member_id] = "Invalid member_id " + str(member_id)
                    return log
                else:
                    user_list.append(user)

        print('USER LIST TOP UPDATE', user_list)
        for user in user_list:

            user_added_id_list.append(user.id)

            existing_user_to_job = User_To_Job.get_single_by_ids(
                session=session,
                user_id=user.id,
                job_id=self.id)
            print('USER LIST TOP UPDATE', user_list)
            if existing_user_to_job:
                # Add user back into job
                if existing_user_to_job.status == 'removed':
                    existing_user_to_job.status = 'active'
                    log['info']['update_member_list'][user.member_id] = "Added"
                    if add_to_session is True:
                        session.add(existing_user_to_job)
                else:
                    log['info']['update_member_list'][user.member_id] = "Unchanged."
                continue

            user_to_job = self.attach_user_to_job(
                session=session,
                user=user,
                add_to_session=add_to_session,
                relation = 'annotator')

            log['info']['update_member_list'][user.member_id] = "Added"

        print(' user_added_id_list', user_added_id_list)
        # careful, user_id not member_id
        remaining_user_to_job_list = User_To_Job.list(
            session=session,
            user_id_ignore_list=user_added_id_list
        )
        print(' remaining_user_to_job_list', remaining_user_to_job_list)
        for rel in remaining_user_to_job_list:
            print('user to job', rel.user_id, rel.job_id, rel.user.first_name, rel.status, add_to_session)
            if rel.status != 'removed':
                rel.status = 'removed'
                print('set to removend', rel.user_id, rel.status)
                session.add(rel)
                # TODO this should be uniform, it's not right now
                # this is update_user_list but we need to add member_id to user_to_job
                # it sounds like this needed to be member_list for current tests so just leaving it for now.
                log['info']['update_member_list'][rel.user_id] = "Removed"

        self.set_cache_by_key(
            cache_key='member_list_ids',
            value=member_list_ids)
        if add_to_session is True:
            session.add(self)

        return log

    def regenerate_member_list_ids(
            self,
            session):
        member_list_ids = User_To_Job.list(
            session=session,
            job=self,
            relation = 'annotator',
            serialize=True)
        return member_list_ids

    def regenerate_reviewer_list_ids(
            self,
            session):
        member_list_ids = User_To_Job.list(
            session=session,
            job=self,
            relation = 'reviewer',
            serialize=True)
        return member_list_ids

    def serialize_trainer_info_default(self,
                                       session,
                                       user_id):

        user_to_job_serialized = None
        user_to_job = User_To_Job.get_single_by_ids(session=session,
                                                    user_id=user_id,
                                                    job_id=self.id)
        if user_to_job:
            user_to_job_serialized = user_to_job.serialize_trainer_info_default()

        guide = None
        if self.guide_default_id:
            guide = self.guide_default.serialize_for_trainer()

        default_userscript = None
        if self.default_userscript:
            default_userscript = self.default_userscript.serialize()

        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'share_type': self.share_type,
            'user_to_job': user_to_job_serialized,
            'guide': guide,
            'default_userscript': default_userscript
        }

    def serialize_minimal_info(self):
        """
        Used to be name and id only, but realizing time created
        and little things there are needed
        """
        return {
            'id': self.id,
            'name': self.name,
            'is_pinned': self.is_pinned,
            'type': self.type,
            'time_created': self.time_created,
            'allow_reviews': self.allow_reviews
        }

    def serialize_for_task(self):
        """serialize
            Use to send job data in the task context.
        :return:
        """
        data = self.serialize_minimal_info()
        if self.ui_schema:
            data['ui_schema'] = self.ui_schema.serialize()
        return data

    # TODO way too much repeating with these serialize functions let's combine it

    def get_attached_dirs(self, session, sync_types=['sync']):
        attached_dirs_rels = session.query(WorkingDir).join(JobWorkingDir).filter(
            JobWorkingDir.job_id == self.id,
            JobWorkingDir.sync_type != 'archived'
        )
        if sync_types:
            attached_dirs_rels.filter(JobWorkingDir.sync_type.in_(sync_types))
        return attached_dirs_rels.all()

    def get_attached_dirs_serialized(self, session):
        attached_dirs_rels = session.query(JobWorkingDir).filter(
            JobWorkingDir.job_id == self.id
        )
        dir_list = [
            {
                'nickname': attachment.working_dir.nickname,
                'directory_id': attachment.working_dir.id,
                'selected': attachment.sync_type
            }
            for attachment in attached_dirs_rels
        ]
        return {
            'attached_directories_list': dir_list
        }

    # INFO DEFAULT
    def serialize_builder_info_default(
            self,
            session,
            user=None):

        # TODO share this with trainer info function
        user_to_job_serialized = None
        if user:
            user_to_job = User_To_Job.get_single_by_ids(session=session,
                                                        user_id=user.id,
                                                        job_id=self.id)
            if user_to_job:
                user_to_job_serialized = user_to_job.serialize_trainer_info_default()

        percent_completed = 0
        tasks_remaining = 0

        if self.stat_count_tasks:
            percent_completed = (self.stat_count_complete / self.stat_count_tasks) * 100
            tasks_remaining = self.stat_count_tasks - self.stat_count_complete
        external_mappings = ExternalMap.get(
            session=session,
            job_id=self.id,
            diffgram_class_string='task_template',
            return_kind='all'
        )
        member_list_ids = None

        if session:
            member_list_ids = self.get_with_cache(
                cache_key='member_list_ids',
                cache_miss_function=self.regenerate_member_list_ids,
                session=session,
                miss_function_args={'session': session})
            reviewer_list_ids = self.get_with_cache(
                cache_key='reviewer_list_ids',
                cache_miss_function=self.regenerate_reviewer_list_ids,
                session=session,
                miss_function_args={'session': session})
        external_mappings_serialized = [x.serialize() for x in external_mappings]

        default_userscript = None
        if self.default_userscript:
            default_userscript = self.default_userscript.serialize()
        exam = None
        if self.exam:
            exam = self.exam.serialize()

        return {
            'id': self.id,
            'name': self.name,
            'exam': exam,
            'type': self.type,
            'ui_schema_id': self.ui_schema_id,
            'share_type': self.share_type,
            'member_list_ids': member_list_ids,
            'reviewer_list_ids': reviewer_list_ids,
            'status': self.status,
            'time_created': self.time_created,
            'time_completed': self.time_completed,
            'user_to_job': user_to_job_serialized,
            'attached_directories_dict': self.get_with_cache(
                cache_key='attached_directories_dict',
                cache_miss_function=self.get_attached_dirs_serialized,
                session=session,
                miss_function_args={'session': session}),
            'external_mappings': external_mappings_serialized,

            'file_count_statistic': self.file_count_statistic,
            'stat_count_tasks': self.stat_count_tasks,
            'stat_count_complete': self.stat_count_complete,
            'percent_completed': percent_completed,
            'tasks_remaining': tasks_remaining,
            'is_live': self.is_live,
            'pending_initial_dir_sync': self.pending_initial_dir_sync,
            'interface_connection': self.interface_connection.serialize() if self.interface_connection else None,

            # For now the SDK uses the /info path
            # So if we want to expose this stuff we need that there
            # maybe something to review in the future

            'file_count': self.file_count,
            'launch_datetime': self.launch_datetime,
            'launch_datetime_deferred': self.launch_datetime_deferred,
            'launch_attempt_log': self.launch_attempt_log,
            'waiting_to_be_launched': self.waiting_to_be_launched,
            'interface_connection_id': self.interface_connection_id,

            # Realizing we want the label dict
            # ie to show the label information (not just ids...)
            'label_dict': self.label_dict,
            'completion_directory_id': self.completion_directory_id,
            'output_dir_action': self.output_dir_action,
            'pro_network': self.pro_network,
            'default_userscript': default_userscript

        }

    # BUILDER EDIT
    def serialize_builder_info_edit(self, session):

        member_list_ids = None
        if session:
            member_list_ids = self.get_with_cache(
                cache_key='member_list_ids',
                cache_miss_function=self.regenerate_member_list_ids,
                session=session,
                miss_function_args={'session': session})
            reviewer_list_ids = self.get_with_cache(
                cache_key='reviewer_list_ids',
                cache_miss_function=self.regenerate_reviewer_list_ids,
                session=session,
                miss_function_args={'session': session})
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'status': self.status,
            'member_list_ids': member_list_ids,
            'reviewer_list_ids': reviewer_list_ids,
            'time_created': self.time_created,
            'time_completed': self.time_completed,

            'label_mode': self.label_mode,
            'attached_directories_dict': self.get_with_cache(
                cache_key='attached_directories_dict',
                cache_miss_function=self.get_attached_dirs_serialized,
                session=session,
                miss_function_args={'session': session}),
            'passes_per_file': self.passes_per_file,
            'share_type': self.share_type,
            'instance_type': self.instance_type,
            'permission': self.permission,
            'category': self.category,
            'type': self.type,
            'pending_initial_dir_sync': self.pending_initial_dir_sync,
            'review_by_human_freqeuncy': self.review_by_human_freqeuncy,
            'allow_reviews': self.allow_reviews,
            'review_chance': self.review_chance * 100,

            'project_string_id': self.project.project_string_id,
            'is_live': self.is_live,

            'file_count': self.file_count,
            'launch_datetime': self.launch_datetime,
            'launch_datetime_deferred': self.launch_datetime_deferred,
            'launch_attempt_log': self.launch_attempt_log,
            'waiting_to_be_launched': self.waiting_to_be_launched,
            'label_file_list': self.label_dict.get('label_file_list'),
            'file_handling': self.file_handling,
            'interface_connection_id': self.interface_connection_id,
            'interface_connection': self.interface_connection.serialize() if self.interface_connection else None,

            'file_count_statistic': self.file_count_statistic,
            'completion_directory_id': self.completion_directory_id,
            'output_dir_action': self.output_dir_action,
            'pro_network': self.pro_network

        }

    def serialize_trainer_info_start(self):

        # Could also have a "no guide provided" option?

        guide = None
        if self.guide_default_id:
            self.guide_default.serialize_for_trainer()

        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'guide': guide,
            'td_api_trainer_basic_training': self.td_api_trainer_basic_training
        }

    def task_list(self,
                  session,
                  status_list: list = None,
                  task_type=None):

        query = session.query(Task).filter(Task.job_id == self.id)

        if task_type:
            query = query.filter(Task.task_type == task_type)

        if status_list:
            query = query.filter(Task.status.in_(status_list))

        return query.all()

    def serialize_for_list_view(self, session=None):

        stat_count_available = None
        if self.stat_count_tasks:
            stat_count_available = self.stat_count_tasks - self.stat_count_complete
        member_list_ids = None
        attached_directories_dict = None
        if session:
            member_list_ids = self.get_with_cache(
                cache_key='member_list_ids',
                cache_miss_function=self.regenerate_member_list_ids,
                session=session,
                miss_function_args={'session': session})
            attached_directories_dict = self.get_with_cache(
                cache_key='attached_directories_dict',
                cache_miss_function=self.get_attached_dirs_serialized,
                session=session,
                miss_function_args={'session': session})
        return {
            'id': self.id,
            'cache_info': self.cache_dict.get('__info') if self.cache_dict else None,
            'name': self.name,
            'time_created': str(self.time_created),
            # str() wrap is for json encoding, see export.py
            'time_updated': str(self.time_updated),
            'time_completed': str(self.time_completed),
            'status': self.status,
            'type': self.type,
            'instance_type': self.instance_type,
            'is_pinned': self.is_pinned,
            'is_live': self.is_live,
            'attached_directories_dict': attached_directories_dict,
            'file_count_statistic': self.file_count_statistic,
            'stat_count_tasks': self.stat_count_tasks,
            'stat_count_complete': self.stat_count_complete,
            'stat_count_available': stat_count_available,
            'share_type': self.share_type,
            'waiting_to_be_launched': self.waiting_to_be_launched,
            'launch_datetime': str(self.launch_datetime),
            'completion_directory_id': self.completion_directory_id,
            'completion_directory': {
                'id': self.completion_directory_id,
                'nickname': self.completion_directory.nickname if self.completion_directory else None
            },
            'output_dir_action': self.output_dir_action,
            'interface_connection': self.interface_connection.serialize() if self.interface_connection else None,
            'label_dict': self.label_dict,
            'member_list_ids': member_list_ids
            # We could include the deferred time too
            # However, intially the deferred time is blank
            # So unless we default that to also equal the launch time?

            # List project name? can't directly call project would need .seralize()
            # 'project' : self.project

        }

    # This is for when we newly create a job
    # Prior to it being launched

    def serialize_new(self):

        return {
            'id': self.id,
            'created_time': self.time_created,
            'status': self.status,
            'name': self.name,
        }

    def update_file_count_statistic(
            self,
            session):
        """
        In theory we could count each file as it gets added
        but that seems prone to off by 1 errors in distributed systems
        context.
        Instead we just query the count,
        and update it here?

        Slight problem is that this statistic could be out if
        the file doesn't get remove properly from the job...

        """

        self.file_count_statistic = WorkingDirFileLink.file_list(
            session=session,
            working_dir_id=self.directory_id,
            counts_only=True,
            limit=None)

        session.add(self)


    def refresh_stat_count_tasks(self, session):
        task_count_available = Task.list(
            session,
            status = 'available',
            job_id = self.id,
            project_id = self.project_id,
            return_mode = "count"
        )
        task_count_complete = Task.list(
            session,
            status = 'complete',
            job_id = self.id,
            project_id = self.project_id,
            return_mode = "count"
        )

        self.stat_count_tasks = task_count_complete + task_count_available
        self.stat_count_complete = task_count_complete
        session.add(self)
        return


    def job_complete_core(
            self,
            session):
        """
        Checks if job is complete 

        TODO Notifications upon completion

        Status changes of job

        """
        # for now we assume the stat here to be accurate.

        if self.stat_count_tasks - self.stat_count_complete != 0:
            return

            # WIP
        if self.type == "Exam":
            # not implemented
            pass

        session.add(self)  # TODO dont add to session like this
        self.status = "complete"
        Event.new_deferred(
            session=session,
            kind='task_template_completed',
            project_id=self.project_id,
            member_id=get_member(session).id if get_member(session) else None,
            job_id=self.id,
            wait_for_commit=True
        )