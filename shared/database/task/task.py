from shared.database.common import *
from shared.database.event.event import Event
from shared.database.task.guide import Guide
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
import shared.database.discussion.discussion_relation as dr
import shared.database.discussion.discussion as discussion
from shared.database.discussion.discussion_relation import DiscussionRelation
from shared.database.discussion.discussion import Discussion
from shared.database.task.task_user import TaskUser
from shared.database.user import User

TASK_STATUSES = {
    'created': 'created',
    'complete': 'complete',
    'in_progress': 'in_progress',
    'review_requested': 'review_requested',
    'in_review': 'in_review',
    'requires_changes': 'requires_changes',
    'deferred': 'deferred',
}
class Task(Base):
    """
    A single unit of work.

    A task is part of a graph of tasks
    Each task has files that may be done multiple times
    We can "denormalize" links later, but for now want to use data structure

    [ ] Differences for different types, ie semantic segmentation?

    """

    __tablename__ = 'task'
    id = Column(BIGINT, primary_key = True)

    is_live = Column(Boolean, default = True)

    # NEW
    """
    template_id = Column(Integer, ForeignKey('task_template.id'))
    template = relationship(	 "Task_Template", 
                             uselist=False,
                             foreign_keys=[template_id])
    """
    # NEW

    is_root = Column(Boolean)
    root_id = Column(Integer, ForeignKey('task.id'))

    def root(self, session):
        return Task.get_by_id(session, self.root_id)

    """
    root = relationship("Task", 
                          uselist=False,
                          foreign_keys=[root_id],
                          cascade="all, delete-orphan",
                          post_update=True)
    """

    parent_id = Column(Integer, ForeignKey('task.id'))

    def parent(self, session):
        return Task.get_by_id(session, self.parent_id)

    """
    parent = relationship("Task", 
                          uselist=False,
                          foreign_keys=[parent_id],
                          cascade="all, delete-orphan",
                          post_update=True) 	# only 1 parent? so uselist=False
    """

    def child_list(self, session):
        return session.query(Task).filter(
            Task.parent_id == self.id).all()

    # Not sure if we need this...
    child_primary_id = Column(Integer, ForeignKey('task.id'))
    child_primary = relationship("Task",
                                 uselist = False,
                                 foreign_keys = [child_primary_id],
                                 cascade = "all, delete-orphan")

    job_id = Column(Integer, ForeignKey('job.id'), index = True)
    job = relationship("Job")

    kind = Column(String, default = 'human')  # human, machine, other?  or store "master" here...
    task_type = Column(String(), default = 'draw')  # may be inherited from job?
    # draw, review, "master"
    job_type = Column(String)  # inherited from job ['Normal', 'Exam', 'Learning']

    status = Column(String(), default = 'created', index = True)
    # Possible Statuses:
    # ['created', 'in_progress', 'review_requested', 'pending_review', 'requires_changes' 'deferred']

    file_original_id = Column(BIGINT, ForeignKey('file.id'))
    file_original = relationship("File", foreign_keys = [file_original_id])

    file_id = Column(BIGINT, ForeignKey('file.id'), index = True)
    file = relationship("File", foreign_keys = [file_id])

    completion_directory_id = Column(Integer, ForeignKey('working_dir.id'))
    completion_directory = relationship("WorkingDir", foreign_keys = [completion_directory_id])

    # The dir where the file for the task is coming from.
    incoming_directory_id = Column(Integer, ForeignKey('working_dir.id'))
    incoming_directory = relationship("WorkingDir", foreign_keys = [incoming_directory_id])

    # TODO may need a "source" directory too

    completion_action = Column(String())

    # A specific task only needs one guide since that's part of
    guide_id = Column(Integer, ForeignKey('guide.id'))
    guide = relationship("Guide")

    # Rates get inherited from job
    # And don't want to cache here since can have multiple rates!

    project_id = Column(Integer, ForeignKey('project.id'), index = True)
    project = relationship("Project")

    # label_file_id_list is stored in job, so
    # if label_split is None then just use that
    # else can assign a specific label
    # Doesn't support split into multiple label but could with label_file_id_list here too...

    # Inherit from job
    label_mode = Column(String)
    # 'closed_and_split_one_label_per_task', 'closed_all_available', 'open'

    # May be different for each task
    # Depending on settings ie from label_mode
    label_dict = Column(MutableDict.as_mutable(JSONEncodedDict),
                        default = {'label_file_list_serialized': [],
                                   'label_file_colour_map': {}})
    # NOTE this also has 'label_file_list' that is an ID list
    # gets populated at job creation?

    # Deprecated, moved to status...
    # available_for_assignment = Column(Boolean, default=True)

    # Cache
    gold_standard_file = Column(MutableDict.as_mutable(JSONEncodedDict))

    # QUESTION should we be using "member" here?
    # Current assumption is that tasks are only done by users which is maybe
    # wrong
    assignee_user_id = Column(Integer, ForeignKey('userbase.id'))
    # assignee_user = relationship("User", back_populates = "task_list" )
    assignee_user = relationship("User",
                                 foreign_keys = [assignee_user_id],
                                 post_update = True)

    # Why post_update=True
    # see https://stackoverflow.com/questions/18284464/sqlalchemy-exc-circulardependencyerror-circular-dependency-detected

    # For credentials...
    # Deprecated, handled at Job level (ie Trainer joining a job...)
    # requirements = None

    # Tracking history, if it gets re assigned
    previous_assignees = Column((ARRAY(Integer)))

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_completed = Column(DateTime)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    # For billing

    # QUESTION allowing for already created ones...

    count_instances_changed = Column(Integer)

    # number_boxes_created = Column(Integer())
    # number_boxes_updated = Column(Integer())
    # number_boxes_deleted = Column(Integer())

    no_boxes_in_image = Column(Boolean)
    reviewed_no_changes = Column(Boolean)

    review_star_rating_average = Column(Float)

    # We default this to be 0 because at least 2 calculations depend
    # on it existing (as 0).
    # I think we can rely on other things like the "state" for example to deteremine
    # if it has been reviewed or not (if that's even needed).
    gold_standard_missing = Column(Integer, default = 0)

    # External ID's for referencing on integrations like Labelbox, Supervisely, etc.
    default_external_map_id = Column(BIGINT, ForeignKey('external_map.id'))
    default_external_map = relationship("ExternalMap",
                                        uselist = False,
                                        foreign_keys = [default_external_map_id])

    @staticmethod
    def get_task_from_job_id(
        session,
        job_id,
        user,
        direction = 'next',
        assign_to_user = False,
        skip_locked = True):
        from methods.task.task.task_update import Task_Update
        query = session.query(Task).filter(
            Task.status == 'available',
            Task.job_id == job_id)

        if direction == 'next':
            query = query.order_by(Task.time_created)

        elif direction == 'previous':
            query = query.order_by(Task.time_created.desc())

        if skip_locked == True:
            query = query.with_for_update(skip_locked = True)

        task = query.first()
        if assign_to_user is True:

            # TODO check if job has open status, or user is assigned to job
            # For now this assumes that the user is already on correct job

            if task:
                task.add_assignee(session, user)
                task_update_manager = Task_Update(
                    session = session,
                    task = task,
                    status = 'in_progress'
                )
                # set status
                task_update_manager.main()
                session.add(task)
                session.add(user)

        return task

    def navigate_tasks_relative_to_given_task(
        session,
        task_id,
        direction = 'next'
    ):

        known_task = Task.get_by_id(session, task_id = task_id)

        query = session.query(Task).filter(
            Task.status != 'archived',
            Task.job_id == known_task.job_id)

        if direction == 'next':
            query = query.filter(Task.time_created > known_task.time_created)
            query = query.order_by(Task.time_created)

        elif direction == 'previous':
            query = query.filter(Task.time_created < known_task.time_created)
            query = query.order_by(Task.time_created.desc())

        discovered_task = query.first()
        return discovered_task

    def get_last_task(
            session,
            user,
            status_allow_list = ["available", "in_progress"],
            job=None):

        last_task = user.last_task
        if last_task:

            if job:
                if last_task.job_id != job.id:
                    return None

            if last_task.status in status_allow_list:
                return last_task

    def add_reviewer(self, session, user):

        self.assignee_user = user
        rel = TaskUser.new(
            session = session,
            user_id = user.id,
            task_id = self.id,
            relation = 'reviewer'
        )
        return rel

    def has_user(self, session, user):

        result = session.query(TaskUser).filter(
            TaskUser.task_id == self.id
        ).all()
        user_id_list = [elm.user_id for elm in result]
        return user.id in user_id_list

    def add_assignee(self, session, user):

        self.assignee_user = user
        rel = TaskUser.new(
            session = session,
            user_id = user.id,
            task_id = self.id,
            relation = 'assignee'
        )
        user.last_task = self
        return rel

    @staticmethod
    def get_related_files(session, task_id):
        """
            Given the task_id, find the next task that is attached to an issue
            sorting by task creation date.
        :param session:
        :param task_id:
        :return: next task ID or None is not next task.
        """
        task = Task.get_by_id(session, task_id = task_id)

        tasks_query = session.query(Task).filter(
            or_(Task)
        )

        return tasks_query.all()

    @staticmethod
    def get_next_task_with_issues(session, task_id):
        """
            Given the task_id, find the next task that is attached to an issue
            sorting by task creation date.
        :param session:
        :param task_id:
        :return: next task ID or None is not next task.
        """
        task = Task.get_by_id(session, task_id = task_id)

        tasks_query = session.query(Task).filter(Task.status != 'archived',
                                                 Task.job_id == task.job_id)
        tasks = tasks_query.all()
        task_ids = [task.id for task in tasks]
        discussions = session.query(dr.DiscussionRelation) \
            .join(discussion.Discussion, dr.DiscussionRelation.discussion_id == discussion.Discussion.id) \
            .filter(dr.DiscussionRelation.task_id.isnot(None)) \
            .filter(dr.DiscussionRelation.task_id.in_(task_ids), discussion.Discussion.status == 'open') \
            .order_by(discussion.Discussion.created_time.desc())

        seen = set()
        task_ids_with_issues = [x.task_id for x in discussions if not (x.task_id in seen or seen.add(x.task_id))]

        if len(task_ids_with_issues) == 0:
            return None

        if task_id not in task_ids_with_issues:
            # If the provided task_id has no issues we simply return the first one that has issues.
            return task_ids_with_issues[0]
        elif task_ids_with_issues.index(task_id) == len(task_ids_with_issues) - 1:
            # If the provded task_id is the last one we circle back to the first task with issues
            return task_ids_with_issues[0]
        else:
            # If the provided task anything else except the last element we return the next task in the list.
            index_current = task_ids_with_issues.index(task_id)
            return task_ids_with_issues[index_current + 1]

    def request_next_task_by_project(
        session,
        project,
        user,
        ignore_task_IDS_list = None,
        status = 'available',
        skip_locked = True,
        task_type = None):

        from shared.database.task.job.user_to_job import User_To_Job
        from shared.database.task.job.job import Job

        if project is None:
            return False

        query = session.query(Task).filter(
            Task.project_id == project.id)

        job_ids_user_is_assigned = User_To_Job.get_job_ids_from_user(
            session = session,
            user_id = user.id)

        job_ids_open_to_all_users = Job.get_job_IDS_open_to_all(
            session = session,
            project = project)

        job_ids_allowed = job_ids_user_is_assigned + job_ids_open_to_all_users

        query = query.filter(Task.job_id.in_(job_ids_allowed))

        if skip_locked == True:
            query = query.with_for_update(skip_locked = True)

        if status:
            query = query.filter(Task.status == status)

        if task_type:
            query = query.filter(Task.task_type == task_type)

        if ignore_task_IDS_list:
            query = query.filter(Task.id.notin_(ignore_task_IDS_list))

        return query.first()

    @staticmethod
    def get_file_ids_related_to_a_task(
        session,
        task_id,
        project_id):

        related_tasks_list = session.query(Task).filter(
            Task.id == task_id,
            Task.project_id == project_id).all()
        allowed_file_id_list = [task.file_id for task in related_tasks_list]
        return allowed_file_id_list

    def get_next_available_task_by_job_id(
        session,
        job_id,
        task_type = None,
        status = 'available',
        ignore_task_IDS_list = None):
        """
        Assumption is we only get tasks == to the status we set
        ie we ignore all other statuses (like archived)

        Caution ignore list is IDs not statuses
        """

        if job_id is None:
            return None

        query = session.query(Task).filter(
            Task.job_id == job_id)

        if status:
            query = query.filter(Task.status == status)

        if task_type:
            query = query.filter(Task.task_type == task_type)

        if ignore_task_IDS_list:
            query = query.filter(Task.id.notin_(ignore_task_IDS_list))

        return query.first()

    def serialize_trainer_annotate(self, session):

        guide = None
        if self.guide_id:
            guide = self.guide.serialize_for_trainer()

        return {
            'id': self.id,
            'job_id': self.job_id,
            'project_id': self.project_id,
            'task_type': self.task_type,
            'job_type': self.job_type,
            'status': self.job_type,
            'file': self.file.serialize_with_annotations(session = session),
            'guide': guide,
            'label_dict': self.label_dict,
            'assignee_user_id': self.assignee_user_id
        }

    def serialize_builder_view_by_id(self, session):

        guide = None
        if self.guide_id:
            guide = self.guide.serialize_for_trainer()

        gold_standard_file = None
        if self.job_type == "Exam" and self.task_type == "review":
            gold_standard_file = self.get_gold_standard_file()

        # I'm not a huge fan of supplying user script this way but for now
        default_userscript = None
        if self.job:
            if self.job.default_userscript:
                default_userscript = self.job.default_userscript.serialize()

        return {
            'id': self.id,
            'job_id': self.job_id,
            'job': self.job.serialize_for_task(),
            'project_string_id' : self.project.project_string_id,
            'task_type': self.task_type,
            'job_type': self.job_type,
            'file': self.file.serialize_with_type(session = session),
            'gold_standard_file': gold_standard_file,
            'guide': guide,
            'label_dict': self.label_dict,
            'status': self.status,
            'time_updated': str(self.time_updated),
            'time_completed': str(self.time_completed),
            'default_userscript': default_userscript,
            'assignee_user_id': self.assignee_user_id
        }

    def get_by_job_and_file(
        session,
        job,
        file,
        return_type = 'first'):

        query = session.query(Task).filter(
            Task.job_id == job.id,
            Task.file_id == file.id,
        )
        if return_type == 'first':
            return query.first()

    @staticmethod
    def list(session,
             task_ids = None,
             status = None,
             date_from = None,
             date_to = None,
             job_id = None,
             incoming_directory_id = None,
             file_id = None,
             project_id = None,
             mode_data = None,
             issues_filter = None,
             return_mode = None,
             limit_count = 25,
             page_number = 0  # 0 is same as no offset
             ):

        query = session.query(Task)
        if task_ids:
            query = query.filter(
                Task.id.in_(task_ids)
            )
        if status and status != 'all':
            query = query.filter(
                Task.status == status
            )
        elif status == 'all':
            query = query.filter(
                Task.status != 'archived'
            )
        else:
            query = query.filter(
                Task.status != 'archived'
            )
        if incoming_directory_id:
            query = query.filter(Task.incoming_directory_id == incoming_directory_id)

        if job_id:
            query = query.filter(Task.job_id == job_id)

            if mode_data == "exam_results":
                # Only show review tasks since this is what would count here?
                # QUESTION do we want to have the job type check here too
                # query = query.filter(Task.task_type == "review", Task.job_type == "Exam")

                # WIP with auto grader, reviews may just be posted on original tasks.
                query = query.filter(Task.job_type == "Exam")

        if date_from:
            date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(Task.time_updated >= date_from)
        if date_to:
            date_to = datetime.datetime.strptime(date_to, "%Y-%m-%d")
            query = query.filter(Task.time_updated <= date_to)

        if file_id:
            query = query.filter(Task.file_id == file_id)

        if project_id:
            query = query.filter(Task.project_id == project_id)

        if return_mode == "query":
            return query

        if return_mode == "count":
            return query.count()

        query = query.options(joinedload(Task.incoming_directory))
        query = query.options(joinedload(Task.job))
        query = query.order_by(Task.time_created)

        if page_number:
            if page_number < 0: page_number = 0
            query = query.offset(page_number * limit_count)

        task_list = query.limit(limit_count).all()

        task_id_list = [task.id for task in task_list]
        if issues_filter:
            if issues_filter == 'open_issues':
                issues_rels_list = session.query(DiscussionRelation).join(Discussion, DiscussionRelation.issue).filter(
                    DiscussionRelation.task_id.in_(task_id_list),
                    Discussion.status == 'open'
                )
                task_with_issues_id_list = [rel.task_id for rel in issues_rels_list]
                task_list = session.query(Task).filter(Task.id.in_(task_with_issues_id_list))
            if issues_filter == 'closed_issues':
                issues_rels_list = session.query(DiscussionRelation).join(Discussion,
                                                                          DiscussionRelation.issue).filter(
                    DiscussionRelation.task_id.in_(task_id_list),
                    Discussion.status == 'closed'
                )
                task_with_issues_id_list = [rel.task_id for rel in issues_rels_list]
                task_list = session.query(Task).filter(Task.id.in_(task_with_issues_id_list))

            if issues_filter == 'issues':
                issues_rels_list = session.query(DiscussionRelation).join(Discussion,
                                                                          DiscussionRelation.issue).filter(
                    DiscussionRelation.task_id.in_(task_id_list),
                )
                task_with_issues_id_list = [rel.task_id for rel in issues_rels_list]
                task_list = session.query(Task).filter(Task.id.in_(task_with_issues_id_list))

        return task_list

    def get_by_id(session,
                  task_id):

        task = session.query(Task).filter(
            Task.id == task_id).first()

        return task

    def serialize_for_list_view_builder(self, session = None):

        file = None
        if session:
            file = self.file.serialize_with_type(session = session)

        return {
            'id': self.id,
            'task_type': self.task_type,
            'job': {
                'id': self.job.id,
                'name': self.job.name
            },
            'status': self.status,
            'incoming_directory': {
                'nickname': self.incoming_directory.nickname if self.incoming_directory else None,
                'id': self.incoming_directory_id
            },
            'time_updated': str(self.time_updated),
            'time_completed': str(self.time_completed),
            'time_created': self.time_created.isoformat(),
            'assignee_user_id': self.assignee_user_id,
            'file': file

        }

    def serialize_for_exam_results(self):

        # TODO get instance averages...

        return {
            'id': self.id,
            'status': self.status,
            'time_updated': self.time_updated,
            'time_completed': self.time_completed,
            'review_star_rating_average': self.review_star_rating_average,
            'gold_standard_missing': self.gold_standard_missing,
            'assignee_user_id': self.assignee_user_id
        }

    def get_gold_standard_file(self):
        """
        Main place getting gold standard is for exam comparisons
        BUT this could be useful for future more advanced auto test auto grade things,
        even for normal work

        """
        gold_standard_file = None

        if self.gold_standard_file:  # Try cache first
            return self.gold_standard_file

        if self.file_original:
            gold_standard_file = self.file_original.serialize_annotations_only()

        return gold_standard_file

    @staticmethod
    def new(session,
            job,
            file_id,
            guide_id,
            label_dict,
            file_original_id,
            kind = 'human',
            task_type = 'draw',
            incoming_directory = None,
            flush_session = True):
        task = Task()
        session.add(task)

        task.is_live = job.is_live

        # # #
        task.job_id = job.id
        task.file_id = file_id
        task.guide_id = guide_id
        task.label_dict = label_dict
        task.file_original_id = file_original_id
        task.completion_directory_id = job.completion_directory_id
        # For now both created and updated times should be the same.
        task.time_created = datetime.datetime.utcnow()
        task.time_updated = datetime.datetime.utcnow()
        if incoming_directory:
            task.incoming_directory_id = incoming_directory.id

        if task_type == 'draw':
            # Set draw tasks to be available instead of
            # default of created
            task.status = 'available'

        # Cache from job
        task.project_id = job.project_id
        task.job_type = job.type
        task.label_mode = job.label_mode
        if flush_session:
            session.flush()
        # Have defaults
        task.kind = kind
        task.task_type = task_type

        if job.stat_count_tasks is None:
            job.stat_count_tasks = 1
        else:
            job.stat_count_tasks += 1

        Event.new_deferred(
            session = session,
            kind = 'task_created',
            project_id = task.project_id,
            task_id = task.id,
            wait_for_commit = True
        )
        session.add(job)
        return task
