from shared.database.common import *
from enum import Enum
from shared.database.source_control.file import File
from shared.database.discussion.discussion_relation import DiscussionRelation
from shared.database.discussion.discussion import Discussion
from shared.database.export import Export

from sqlalchemy import asc, desc
from sqlalchemy import or_
from sqlalchemy import and_
from shared.regular import regular_log
from shared.database.user import UserbaseProject
from shared.permissions.policy_engine.policy_engine import PolicyEngine, PermissionResultObjectSet
from shared.database.source_control.dataset_perms import DatasetPermissions
from shared.database.tag.tag import Tag

VALID_ACCESS_TYPES = ['project', 'restricted']


class WorkingDir(Base):
    """

    """
    __tablename__ = 'working_dir'

    id = Column(Integer, primary_key = True)
    created_time = Column(DateTime, default = datetime.datetime.utcnow)

    archived = Column(Boolean)  # (similar to soft_delete)

    has_changes = Column(Boolean)

    # Added string instead  of boolean since we can expand this to new types if needed in the future.
    type = Column(String())  # ["project_default", "standard"]

    nickname = Column(String())

    # possible values: ['project', 'restricted']
    access_type = Column(String(), default = 'project')

    count_changes = Column(Integer, default = 0)

    user_id = Column(Integer, ForeignKey('userbase.id'))
    user = relationship("User")

    file_limit_time = Column(Integer)
    # Context: caching checks on limits (ie number uploaded), ie so we don't
    # check it 1000 times for 1000 sequential uploads

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", foreign_keys = [project_id])

    export_list = relationship("Export")

    label_file_colour_map = Column(MutableDict.as_mutable(JSONEncodedDict),
                                   default = {})

    jobs_to_sync = Column(MutableDict.as_mutable(JSONEncodedDict), default = {'job_ids': []})

    # External ID's for referencing on integrations like Labelbox, Supervisely, etc.
    default_external_map_id = Column(BIGINT, ForeignKey('external_map.id'))
    default_external_map = relationship("ExternalMap",
                                        uselist = False,
                                        foreign_keys = [default_external_map_id])

    @staticmethod
    def get_permissions_list() -> list:
        result = []
        for elm in list(DatasetPermissions):
            result.append(elm.value)
        return result

    @staticmethod
    def new_user_working_dir(
        session,
        branch,  # branch is sorta deprecated...
        project,
        user,
        latest_version = None,
        prior_working_dir_id = None,
        project_default_dir = False
    ):
        """
        Create a new working dir for user for a project


        """
        start_time = time.time()

        working_dir = WorkingDir()
        working_dir.user_id = user.id
        working_dir.project_id = project.id
        working_dir.type = 'standard'
        if project_default_dir:
            working_dir.type = 'project_default'

        session.add(working_dir)
        session.flush()

        if prior_working_dir_id:
            file_list = WorkingDirFileLink.file_list(session,
                                                     prior_working_dir_id,
                                                     limit = None)

            for file in file_list:

                if file.child_primary_id:
                    continue

                WorkingDirFileLink.add(session, working_dir.id, file)

        else:
            if latest_version:
                recursively_visit_previous_versions(session, working_dir, latest_version)

                working_dir.latest_version = latest_version

        UserbaseProject.set_working_dir(session,
                                        user.id,
                                        project.id,
                                        working_dir.id)

        end_time = time.time()

        return working_dir

    @staticmethod
    def list(
        session,
        project_id,
        member,
        exclude_archived = True,
        limit = None,
        return_kind = "objects",
        date_to = None,  # datetime
        date_from = None,  # datetime
        date_to_string: str = None,
        date_from_string: str = None,
        nickname: str = None,
        nickname_match_type: str = "ilike",  # substring and helps if case Aa is off
        order_by_class_and_attribute = None,
        order_by_direction = desc,

    ):
        """
            Lists directories/datasets in a project
        :param session:
        :param project_id:
        :param exclude_archived:
        :param limit:
        :param return_kind:
        :param date_to:
        :param date_from:
        :param date_to_string:
        :param date_from_string:
        :param nickname:
        :param nickname_match_type:
        :param order_by_class_and_attribute:
        :param order_by_direction:
        :return:
        """
        from shared.database.project import Project
        project = Project.get_by_id(session = session, id = project_id)
        query = session.query(WorkingDir).filter(
            WorkingDir.project_id == project_id,
            or_(WorkingDir.archived == False, WorkingDir.archived.is_(None))

        )

        from shared.database.permissions.roles import ValidObjectTypes

        # Permissions: get datasets that user can see
        policy_engine = PolicyEngine(session = session, project = project)
        perm_result = policy_engine.get_allowed_object_id_list(
            member = member,
            object_type = ValidObjectTypes.dataset,
            perm = DatasetPermissions.dataset_view
        )
        print('allow all', perm_result.allow_all, perm_result.allowed_object_id_list)

        if nickname:
            if nickname_match_type == "ilike":
                nickname_search = f"%{nickname}%"
                query = query.filter(WorkingDir.nickname.ilike(nickname_search))
            else:
                query = query.filter(WorkingDir.nickname == nickname)

        if date_from or date_to:
            # TODO this is missing the "AND" joint thing for date_from
            if date_from:
                query = query.filter(WorkingDir.created_time >= date_from)

            if date_to:
                query = query.filter(WorkingDir.created_time <= date_to)
        else:
            query = regular_methods.regular_query(
                query = query,
                date_from_string = date_from_string,
                date_to_string = date_to_string,
                base_class = WorkingDir,
                created_time_string = 'created_time'
            )

        if not perm_result.allow_all:
            query = query.filter(
                WorkingDir.id.in_(perm_result.allowed_object_id_list)
            )
        # Must call order by before limit / offset?
        if order_by_class_and_attribute:
            query = query.order_by(
                order_by_direction(order_by_class_and_attribute))

        if return_kind == "count":
            if limit is not None:
                return query.limit(limit).count()
            else:
                return query.count()
        if return_kind == "objects":
            if limit is not None:
                return query.limit(limit).all()
            else:
                return query.all()

    # TODO is this still right?
    # Deprecated maybe since label_file_list is gone
    def build_label_list(self):
        label_list = []
        for file in self.label_file_list:
            if file.state != "removed":
                label_list.append(file.label.serialize_PUBLIC())
        return label_list

    def build_video_list(self):
        video_list = []
        for file in self.video_file_list:
            if file.state != "removed":
                video_list.append(file.video.serialize_PUBLIC())
        return video_list

    def serialize_simple(self):

        return {
            'id': self.id,
            'nickname': self.nickname
        }

    def serialize(self):

        return {
            'id': self.id,
            'directory_id': self.id,  # hack to remove at some point
            'nickname': self.nickname,
            'jobs_to_sync': self.jobs_to_sync,
            'has_changes': self.has_changes,
            'created_time': self.created_time.isoformat()
        }

    def serialize_with_labels(self):
        return {
            'id': self.id,
            'has_changes': self.has_changes,
            'label_list': self.build_label_list()
        }

    def count(self, session, file_type):
        # TODO, is this method deprecated in favour of
        # of WorkingDirFileLink.file_list(counts_only=True)
        # problem with doing count here is can't do fine grained analysis

        return session.query(WorkingDirFileLink).filter(
            WorkingDirFileLink.working_dir_id == self.id,
            WorkingDirFileLink.type == file_type).count()

    def verify_directory_in_project(session, project, directory_id):
        """
        Assumes that access to project == access to directory
        So if the directory is attached the project than there is access

        Other ways we could do this but this seems to work as a basic check
        Future perhaps permissions on individual directories
        """
        directory = session.query(WorkingDir).filter(
            WorkingDir.project_id == project.id,
            WorkingDir.id == directory_id).first()
        if directory:
            return True

        return False

    @staticmethod
    def get(
        session,
        directory_id,
        project_id):

        directory = session.query(WorkingDir).filter(
            WorkingDir.project_id == project_id,
            WorkingDir.id == directory_id).first()
        return directory

    @staticmethod
    def get_by_id(
        session,
        directory_id):

        directory = session.query(WorkingDir).filter(WorkingDir.id == directory_id).first()
        return directory

    @staticmethod
    def get_with_fallback(
        session,
        project,
        directory_id = None):
        """
        If none, uses project default

        Also returns false if directory is None

        TODO
            1) return log/error message (ie that we are printing)
                -> instead of just False, so as to make debugging easier
                (this function is usually quite low level and for expected
                True cases can have surprising upstream results)
        """

        if project is None:
            print('[get_with_fallback], project is None')
            return False

        if directory_id is None:

            directory = project.directory_default
            return directory

        else:

            directory = WorkingDir.get(
                session = session,
                directory_id = directory_id,
                project_id = project.id)

            if directory is None:
                print('[get_with_fallback] bad project & directory combo')
                return False
            else:
                return directory

    @staticmethod
    def new_blank_directory(session,
                            project = None,  # deprecated arg pending removal
                            user = None,
                            latest_version = None,
                            prior_working_dir_id = None,
                            nickname = None,
                            access_type = None,
                            project_id = None,
                            project_default = False
                            ):
        working_dir = WorkingDir(
            nickname = nickname,
            project_id = project_id,
            access_type = access_type,
            type = 'standard'
        )
        if project_default:
            working_dir.type = 'project_default'

        session.add(working_dir)
        session.flush()

        return working_dir

    def add_tags(
        self,
        tag_list,
        session,
        project,
        log):

        if len(tag_list) > 100:
            log['error']['tag_list_length'] = f"Over limit, tags sent: {len(tag_list)}"
            return log

        for name in tag_list:

            tag = Tag.get_or_new(
                name = name,
                project_id = project.id,
                session = session)

            if tag.id is None:
                session.add(tag)

            dataset_tag = tag.add_to_dataset(dataset_id = self.id, session = session)

            session.add(dataset_tag)
            log['success'] = True
            # log['dataset_tag'] = dataset_tag.serialize()

        return log


class WorkingDirFileLink(Base):
    __tablename__ = 'workingdir_file_link'

    """

    Moved away from using association proxy seems to be fairly slow / limited

    TODO should we have project in here too
    Now that we generally restrict directories to have a project?
    """

    working_dir_id = Column(Integer, ForeignKey('working_dir.id'), primary_key = True)
    file_id = Column(Integer, ForeignKey('file.id'), primary_key = True)

    file = relationship("File")

    # Cache here for speed
    type = Column(String())  # == file.type, ie "image", "video", etc.... wonder if should have type frame
    committed = Column(Boolean)

    count = Column(Integer)

    created_time = Column(DateTime, default = datetime.datetime.utcnow)
    last_time = Column(DateTime, onupdate = datetime.datetime.utcnow)

    # This is more for adding stuff
    # Not for getting file directly
    def file_link(session, working_dir_id, file_id):
        file_link = session.query(WorkingDirFileLink).filter(
            WorkingDirFileLink.working_dir_id == working_dir_id,
            WorkingDirFileLink.file_id == file_id).first()
        return file_link

    def remove(session, working_dir_id, file_id):
        file_link = WorkingDirFileLink.file_link(session, working_dir_id, file_id)

        if file_link:
            session.delete(file_link)

    def add(session, working_dir_id, file):
        # need full file object
        # for type and committed
        file_link = WorkingDirFileLink(working_dir_id = working_dir_id,
                                       file_id = file.id,
                                       type = file.type,
                                       committed = file.committed)
        session.add(file_link)

    def commit(session, working_dir_id, file):
        file_link = WorkingDirFileLink.file_link(session, working_dir_id, file.id)
        file_link.committed = True
        session.add(file_link)

    # TODO merge this with above too similar of function
    # to only have "list" as extra thing
    # CAREFUL LIST  see above
    def get_list_sub_query(
        session,
        directory_id_list: list,  # assumes integer ids
        type = None):

        # CAREFUL LIST
        query = session.query(WorkingDirFileLink).filter(
            WorkingDirFileLink.working_dir_id.in_(directory_id_list))

        if type is None:
            return query.subquery('file_link_sub_query')

        return query.filter(WorkingDirFileLink.type == type).subquery(
            'file_link_sub_query')

    def get_sub_query(session, working_dir_id, type = None):

        if working_dir_id is None:
            return False

        query = session.query(WorkingDirFileLink).filter(
            WorkingDirFileLink.working_dir_id == working_dir_id)

        if type is None:
            return query.subquery('file_link_sub_query')

        # TODO not clear benefit of doing this here
        if isinstance(type, str):
            return query.filter(WorkingDirFileLink.type == type).subquery(
                'file_link_sub_query')

        if isinstance(type, list):
            return query.filter(WorkingDirFileLink.type.in_(type)).subquery(
                'file_link_sub_query')

    # TODO would like to have this be part of a Directory() method would be easier to type
    # TODO too many options here, gotta maybe think about a way to
    # break this up.

    @staticmethod
    def file_list(session,
                  working_dir_id = None,
                  root_files_only = False,
                  limit = 25,
                  type = None,
                  ann_is_complete = None,
                  counts_only = False,
                  exclude_removed = True,
                  date_from = None,
                  date_to = None,
                  issues_filter = None,
                  directory_list = None,
                  time_kind = "created",
                  has_some_machine_made_instances = None,
                  order_by_class_and_attribute = None,  # File.original_filename
                  order_by_direction = asc,
                  offset = None,
                  return_mode = None,
                  job_id = None,
                  count_before_limit = False,
                  file_view_mode = False,
                  ignore_id_list = None,
                  original_filename = None,
                  original_filename_match_type = "ilike"  # Set to None to get exact match
                  ):
        """

        order_by_direction assumed to be either asc or desc
        from sqlalchemy, treated as a function ie asc(order_by_class_and_attribute)

        Work in progress
        TODO maybe move some of core data logic from file thing back here
        AS LONG AS using flags properly

        date_from expects a type datetime object?

        Is it safe that if there's a job id, the directory is ignored?
        I'm trying to think of a case where we would want to filter by both.
        """

        # TODO is it save to have .state != removed here?

        # Assumes working dir....

        if job_id:
            if not order_by_class_and_attribute:
                query = session.query(File).distinct(File.id).filter(File.job_id == job_id)
            else:
                query = session.query(File).filter(File.job_id == job_id)

        else:
            if directory_list is None:
                if working_dir_id is None: return None
                file_link_sub_query = WorkingDirFileLink.get_sub_query(
                    session, working_dir_id, type)

            else:
                directory_id_list = [directory.id for directory in directory_list]
                file_link_sub_query = WorkingDirFileLink.get_list_sub_query(
                    session, directory_id_list, type)
            if not order_by_class_and_attribute:
                query = session.query(File).distinct(File.id).filter(
                    File.id == file_link_sub_query.c.file_id)
            else:
                query = session.query(File).filter(
                    File.id == file_link_sub_query.c.file_id)

        if exclude_removed is True:
            query = query.filter(File.state != "removed")

        # if an image with a video id, exclude it)
        # Would prefer a better way to handle this
        # BUT at least this is all in one query...
        if isinstance(type, list):
            query = query.filter(
                File.type.in_(type)
            )

        if original_filename is not None:
            if original_filename_match_type == "ilike":
                original_filename_search = f"%{original_filename}%"
                query = query.filter(File.original_filename.ilike(original_filename_search))
            else:
                query = query.filter(File.original_filename == original_filename)

        # Careful if x is "False" then this will fail with is not None!
        if ann_is_complete is not None:

            if ann_is_complete is True:
                query = query.filter(File.ann_is_complete == True)

            if ann_is_complete is False:
                query = query.filter(or_(File.ann_is_complete != True,
                                         File.ann_is_complete == None))

        if has_some_machine_made_instances is not None:
            # if ann_is_complete is None then effectively all

            if has_some_machine_made_instances is True:
                query = query.filter(File.has_some_machine_made_instances == True)

            if has_some_machine_made_instances is False:
                query = query.filter(or_(File.has_some_machine_made_instances != True,
                                         File.has_some_machine_made_instances == None))

        if root_files_only is True:
            # This works for images too since
            # A regular image has no parent file

            # For now by default we exclude type of label
            # As labels aren't really used in this context
            query = query.filter(File.video_parent_file_id == None,
                                 File.type != 'label')

        # TODO clarify task mode is related to attaching to a job
        # And not necessarily viewing files from a task?
        if ignore_id_list:
            query = query.filter(File.id.notin_(ignore_id_list))

        if file_view_mode == "changes":
            query = query.filter(File.committed == None,
                                 or_(and_(File.state == "removed", File.parent_id != None),
                                     File.state != "removed"))

        if issues_filter:
            file_list = query.all()
            file_list_ids = [file.id for file in file_list]

            issue_rels_query = session.query(DiscussionRelation).join(Discussion, DiscussionRelation.issue).filter(
                DiscussionRelation.file_id.in_(file_list_ids)
            )
            if issues_filter == 'issues':
                issue_rels = issue_rels_query.all()

            elif issues_filter == 'open_issues':
                issue_rels_query = issue_rels_query.filter(Discussion.status == 'open')
                issue_rels = issue_rels_query.all()

            elif issues_filter == 'closed_issues':
                issue_rels_query = issue_rels_query.filter(Discussion.status == 'closed')
                issue_rels = issue_rels_query.all()

            file_with_issues_id_list = [rel.file_id for rel in issue_rels]
            query = query.filter(File.id.in_(file_with_issues_id_list))

        # Do we want to use created_time
        # or time_last_updated

        if time_kind == "created":
            datetime_property = File.created_time

        if time_kind == "updated":
            datetime_property = File.time_last_updated

        # Do And if both...

        if date_from and date_to:
            query = query.filter(
                datetime_property >= date_from,
                datetime_property <= date_to)
        else:
            if date_from:
                query = query.filter(datetime_property >= date_from)

            if date_to:
                query = query.filter(datetime_property <= date_to)

        if issues_filter:
            file_list = query.all()
            file_list_ids = [file.id for file in file_list]
            if issues_filter == 'issues':
                issue_rels = session.query(DiscussionRelation).join(Discussion, DiscussionRelation.issue).filter(
                    DiscussionRelation.file_id.in_(file_list_ids)
                ).all()
            elif issues_filter == 'open_issues':
                issue_rels = session.query(DiscussionRelation).join(Discussion, DiscussionRelation.issue).filter(
                    DiscussionRelation.file_id.in_(file_list_ids),
                    Discussion.status == 'open'
                ).all()
            elif issues_filter == 'closed_issues':
                issue_rels = session.query(DiscussionRelation).join(Discussion, DiscussionRelation.issue).filter(
                    DiscussionRelation.file_id.in_(file_list_ids),
                    Discussion.status == 'closed'
                ).all()
            file_with_issues_id_list = [rel.file_id for rel in issue_rels]
            query = query.filter(File.id.in_(file_with_issues_id_list))
        # Must call order by before limit / offset?
        if order_by_class_and_attribute:
            query = query.order_by(
                order_by_direction(order_by_class_and_attribute))

        count = None
        if count_before_limit is True:
            # concerend about performance, but maybe something we can cache...
            count = query.count()

        if limit is not None:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        if return_mode == "query":
            return query, count

        if counts_only is True:
            return query.count()

        if counts_only is False:
            return query.all()

    def image_file_list_from_video(
        session,
        video_parent_file_id,
        limit = None,
        start = None,
        end = None,
        order_by_frame = True,  # bool
        has_count_instances_changed = False,
        return_mode = "objects"
    ):
        """
        Work in progress
        TODO maybe move some of core data logic from file thing back here
        AS LONG AS using flags properly

        has_count_instances_changed means it has at least 1 instance changed
        does 0 flag as null too?
        """

        # Do we want to use ann_is_complete here?
        # I guess would matter for automatic ones, but less so for user ones?
        # Maybe a reason to default to False insteasd of None?

        # How do we want to handle purposely uploaded ones like
        # image is inference? just anoter flag?

        # TODO what is the equivlent in sql alchmey to "All"
        # ie None works as all for limits, but not for say an ==

        # TODO or statment for ann_is_complete is False

        # We already check video_parent_file is in directory we want
        # So for other stuff, if we assume that that a video file can
        # only have one parent, we shouldn't need to check directory right?

        # Careful video_id  for *file*_video_id
        query = session.query(File).filter(
            File.video_parent_file_id == video_parent_file_id,
            File.state != "removed").limit(limit)

        if has_count_instances_changed == True:
            # note change from "has" for useful function signature
            # vs property without "has"
            query = query.filter(File.count_instances_changed != 0)

        if order_by_frame:  # assumes assending?
            query = query.order_by(File.frame_number)

        # Careful, python treats 0 as False which results in artificial slow down
        # Low priority todo handle if only one or other / check better here?

        if start or end:
            query = query.filter(
                File.frame_number >= start,
                File.frame_number <= end)

        if return_mode == "objects":
            return query.limit(limit).all()

        if return_mode == "query":
            return query.limit(limit)

    @staticmethod
    def file_link_update(session,
                         add_or_remove,
                         incoming_directory,
                         directory,
                         file_id,
                         job,
                         log = None
                         ):
        """
        Constructs or removes basic file directory link

        Arguments
            session, db session
            add_or_remove, string
            incoming_directory, class WorkingDir object, the file we are adding
            log, regular log dict
            directory, class WorkingDir object
            file_id,

        Returns
            result, bool
            log, updated log

        """
        if log is None:
            log = regular_log.default_api_log()

        # TODO this feels like it should be shared with other methods

        # This does need to be here though
        # As we may have a case where there is not previous file
        # ie the file is "new" to the user's directory

        # Check if the file already exists in directory
        # Do we still need this?

        # TODO clarify diff between incoming and existing
        add_or_remove = add_or_remove.lower()
        if add_or_remove not in ["add", "remove"]:
            log['error']['kind'] = "Invalid add_or_remove"
            return False, log

        # New directory we want to add the file to already
        # May have the file link
        existing_file_link = WorkingDirFileLink.file_link(
            session, directory.id, file_id)
        if add_or_remove == "add":

            # Note info not error.
            if existing_file_link:
                log['info']['file_link'] = "File link already exists"
                return True, log

            # Only relevant for the ADD operation.
            incoming_file_link = WorkingDirFileLink.file_link(
                session, incoming_directory.id, file_id)
            if not incoming_file_link:
                log['error']['file_link'] = "File link not in incoming directory." + \
                                            "Are you on the "
                return False, log

            # Limit, issue is not storing files
            # But how we handle completion afterwards.

            # TODO handle if person wants to change job completion directory

            # Double check this: Commenting this logic out as now files can come from multiple directories

            # if job.completion_directory_id != incoming_file_link.working_dir_id:
            # 	log['error']['job'] = "All files in a job must be from same directory."
            # 	return False, log

            WorkingDirFileLink.add(session,
                                   directory.id,
                                   incoming_file_link.file)

            return True, log

        if add_or_remove == "remove":

            if not existing_file_link:
                log['error']['file_link'] = "No File link to remove"
                return False, log

            WorkingDirFileLink.remove(session,
                                      directory.id,
                                      existing_file_link.file_id)

        return True, log
