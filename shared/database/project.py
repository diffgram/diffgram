from enum import Enum
from shared.database.common import *
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.database.user import UserbaseProject
from shared.database.source_control.file import File
from shared.database.source_control.working_dir import WorkingDir
from shared.database.project_directory_list import Project_Directory_List
from shared.database.event.event import Event
from shared.database.report.report_dashboard import ReportDashboard
from shared.database.org.org import Org
from shared.database.account.account import Account
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from shared.database.labels.label_schema import LabelSchemaLink, LabelSchema
from shared.database.labels.label import Label
from shared.regular import regular_log
from shared.database.tag.tag import Tag
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()
PROJECT_DEFAULT_ROLES = ['admin', 'editor', 'viewer']


class Project(Base, Caching):
    """
    serialize(self)
    get_project(session, project_string_id)
    get_users_current_project(session)
    """

    __tablename__ = 'project'

    id = Column(Integer, primary_key = True)
    name = Column(String(250))

    is_public = Column(Boolean)

    goal = Column(String())

    # TODO update / add these fields in sandbox DB
    deletion_pending = Column(Boolean)  # NEW, renamed from soft_remove
    deletion_id = Column(Integer, ForeignKey('deletion.id'))
    deletion = relationship("Deletion", foreign_keys = [deletion_id])

    highest_ai_version_number = Column(Integer, default = 0)

    star_count = Column(Integer, default = 0)
    star_list = relationship("ProjectStar")

    latest_issue_number = Column(Integer, default = 0)
    discussion_list = relationship("Discussion", back_populates = "project")

    credit_balance = Column(Float())  # Maybe this should be by billing account or something?
    project_string_id = Column(String(100), index = True)  # Added index

    user_primary_id = Column(Integer, ForeignKey('userbase.id'))
    user_primary = relationship("User", foreign_keys = [user_primary_id])
    # TODO clarify difference between user primary
    # and member created?

    users = association_proxy('userbase_projects', 'userbase')

    # TODO review, not being used?
    # activity_list = relationship("Activity", back_populates="project")

    directory_list = relationship("Project_Directory_List")

    directory_default_id = Column(Integer, ForeignKey('working_dir.id'))
    directory_default = relationship("WorkingDir",
                                     foreign_keys = [directory_default_id])

    default_report_dashboard_id = Column(Integer, ForeignKey('report_dashboard.id'))
    # order of this loading is not quite right
    # default_report_dashboard = relationship("ReportDashboard",
    #								foreign_keys=[default_report_dashboard_id])

    api_billing_enabled = Column(Boolean)

    tag_list = association_proxy('project_tag_junction', 'tag')

    annotations_feedback_loop_trigger_check = Column(Boolean())

    # TODO review this
    # Does every project have a seperate settings table?
    settings = relationship("Project_settings", uselist = False, back_populates = "project")

    settings_input_video_fps = Column(Integer, default = 30)  # ie 10,  0 == all

    readme = Column(String())

    export_list = relationship("Export")

    ###
    # We may want to link directly to version?

    # This is member, but for now the only member who can create a project
    # is a User, because an API auth is for a project scope at the moment
    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    label_dict = Column(MutableDict.as_mutable(JSONEncodedDict), default = {})

    cache_dict = Column(MutableDict.as_mutable(JSONEncodedDict),
                        default = {})

    # cache_expiry = Column(Integer)

    # External ID's for referencing on integrations like Labelbox, Supervisely, etc.
    default_external_map_id = Column(BIGINT, ForeignKey('external_map.id'))  # TODO: add to production
    default_external_map = relationship("ExternalMap",
                                        uselist = False,
                                        foreign_keys = [default_external_map_id])

    org_id = Column(Integer, ForeignKey('org.id'))
    org = relationship(Org, foreign_keys = [org_id])

    account_id = Column(Integer, ForeignKey('account.id'))
    account = relationship("Account", foreign_keys = [account_id])

    plan_id = Column(Integer, ForeignKey('plan.id'))
    plan = relationship('Plan',
                        foreign_keys = [plan_id])

    @staticmethod
    def get_permissions_list() -> list:
        result = []
        for elm in list(ProjectValidPermissions):
            result.append(elm.value)
        return result

    @staticmethod
    def new(session,
            name: str,
            project_string_id: str,
            goal: str,
            user,
            member_created,
            ):

        # Avoid circular import
        # Maybe in future Project_permissions class could be part of project
        from shared.permissions.project_permissions import Project_permissions

        project = Project(  # Base object
            name = name,
            project_string_id = project_string_id,
            goal = goal,
            user_primary = user,  # Assumed to be primary
            member_created = member_created
        )

        # Permissions and user associations
        user.projects.append(project)
        user.current_project_string_id = project_string_id
        user.project_current = project

        log = regular_log.default()
        permission_result, log = Project_permissions.add(
            session = session,
            permission = "admin",
            user = user,
            sub_type = project_string_id,
            log = log)
        if regular_log.log_has_error(log):
            logger.error(log)
            return None

        session.add(user, project)

        session.flush()

        schema = LabelSchema.new(
            session = session,
            name = 'Default Schema',
            project_id = project.id,
            member_created_id = member_created.id,
            is_default = True
        )

        member_id = user.member_id

        Event.new(
            session = session,
            kind = "new_project",
            member_id = member_id,
            success = True,
            project_id = project.id,
            email = user.email  # Caution, assumes user object is available
        )

        project.directory_default = WorkingDir.new_user_working_dir(
            session, None, project, user, project_default_dir = True)

        report_dashboard = ReportDashboard.new(project_id = project.id)
        session.add(report_dashboard)

        session.flush()  # Needed to work with adding default directory

        # careful this expects a default dir already assigned
        Project_Directory_List.add_default(
            session = session,
            working_dir_id = project.directory_default.id,
            project = project)

        ### Account  ###
        account_list = Account.get_list(
            session = session,
            user_id = user.id,
            mode_trainer_or_builder = "builder",
            account_type = "billing",
            by_primary_user = True)

        # TODO assumes first in list.
        if account_list:
            project.account = account_list[0]

            # This needs work
            # Rationale is we want to make it easy for someone who has billing
            # enabled to create a new project but this is making a lot of assumptions
            if project.account.payment_method_on_file is True:
                project.api_billing_enabled = True

        else:
            account = Account.account_new_core(
                session = session,
                primary_user = user,
                mode_trainer_or_builder = "builder",
                account_type = "billing",
                nickname = "My Account")

            project.account = account

        ### PLAN ###

        if user.default_plan_id:
            project.plan = user.default_plan

        return project

    @staticmethod
    def get_by_name(session, name):
        project = session.query(Project).filter(
            name == name
        ).first()
        return project

    def has_member(self, member_id) -> bool:
        for user in self.users:
            if user.member_id == member_id:
                return True
        return False

    @staticmethod
    def list(
        session,
        user = None,
        mode = "from_user",  # [from_user, super_admin, from_account_id]
        limit = 60,
        return_kind = "objects",
        date_to = None,
        date_from = None,
        account_id = None
    ):
        """
        Defaults to being 'from_user' can also be 'super_admin' to get all projects

        Replacement for the association table ref (.projects)
        I'm not a huge fan of this being dedicated to a "by user"
        Directional
          * Consider UserbaseProject available to Project,
          I'm assuming that circular import may be a prolem
          * Generic method for all the "common" query things like
          the date from filter and limit etc. etc. feel like we
          need a better pattern there.

        """

        if mode == "from_user":
            if user is None: return False

            # Keep in mind this many to many so sub query first
            sub_query = session.query(UserbaseProject).filter(
                UserbaseProject.user_id == user.id)

            sub_query = sub_query.subquery()

            query = session.query(Project).filter(
                Project.id == sub_query.c.project_id)

        elif mode == "super_admin":
            query = session.query(Project)

        elif mode == "from_account_id":
            query = session.query(Project).filter(
                Project.account_id == account_id)

        # Theory that when a user gets added
        # may be more relevant by default then the original project
        # creation time itself?... this could be complicated though...

        # sub_query = sub_query.order_by(UserbaseProject.created_time)
        # not clear how to order by correctly using a sub query

        datetime_property = Project.time_created

        if date_from and date_to:
            query = query.filter(
                datetime_property >= date_from,
                datetime_property <= date_to)
        else:
            if date_from:
                query = query.filter(datetime_property >= date_from)

            if date_to:
                query = query.filter(datetime_property <= date_to)

        query = query.order_by(Project.id.desc())

        if return_kind == "count":
            return query.limit(limit).count()

        if return_kind == "objects":
            return query.limit(limit).all()

    def regenerate_preview_file_list(self):
        """
        Returns
            Empty array if no files
            Otherwise array of preview files
            Treating like a "cache" thing so can query this to
            get new ones.

        Thought process is that
            a) We may want to use files for other things
            b) Not clear if we want to use preview image or not
            c) More work to try and parse it into URLs only upfront,
              and not clear of benefit since not actually storing that much data
              and we may *want* to say get a preview of instances or
              something else too...

        Assumes:
            using self.session
            default directory
        """

        preview_file_list = []
        if self.session is None:
            return preview_file_list

        file_list = WorkingDirFileLink.file_list(
            session = self.session,
            working_dir_id = self.directory_default_id,
            limit = 3,
            type = ['image', 'video'],
            root_files_only = True  # Excludes labels  at time of writing
        )

        if not file_list:
            return preview_file_list

        for file in file_list:
            preview_file_list.append(file.serialize_with_type(self.session))

        return preview_file_list

    def create_default_roles(self, session):
        from shared.database.permissions.roles import Role
        for role in PROJECT_DEFAULT_ROLES:
            # We create empty permissions because permissions will be managed in code for default roles.
            role = Role.new(
                session = session,
                permissions_list = [],
                name = role,
                project_id = self.id
            )

    def regenerate_member_list(self):

        members_list = []
        for user in self.users:
            members_list.append(
                user.serialize_with_permission(self.project_string_id))
        return members_list

    def regenerate_member_list_cache(self):
        """
        Concrete

        Does not add to session. Assumes cache_dict exists.
        """
        self.cache_dict['member_list'] = self.regenerate_member_list()
        return self.cache_dict['member_list']

    def regenerate_directory_list_cache(self):
        return self.regenerate_cache_by_key(
            'directory_list',
            self.gen_initial_dir_list)

    def refresh_label_dict(self, session):

        file_list = WorkingDirFileLink.file_list(
            session = session,
            working_dir_id = self.directory_default_id,
            limit = 10000000,
            type = "label",
            exclude_removed = False)  # eg for permissions
        if not self.label_dict:
            self.label_dict = {}
        self.label_dict['label_file_id_list'] = [file.id for file in file_list]

    def serialize(self,
                  session = None):
        """
        April 3, 2020
            project.serialize() is called in a bunch of places
            where we don't need session yet so assume None.
        """

        # self.clear_cache()

        settings = None
        if self.settings:
            settings = self.settings.serialize()

        user_primary = None
        if self.user_primary:
            user_primary = self.user_primary.serialize_username_only()

        time_created = None
        if self.time_created:
            time_created = self.time_created.isoformat()

        self.session = None
        if session:
            self.session = session

        project = {
            'id': self.id,
            'cache_info': self.cache_dict.get('__info') if self.cache_dict else None,
            'settings': settings,
            'star_count': self.star_count,
            'name': self.name,
            'credit_balance': self.credit_balance,
            'highest_ai_version_number': self.highest_ai_version_number,
            'images_count': True,  # TODO Get right stats...
            'labels_count': True,
            'project_string_id': self.project_string_id,
            'readme': self.readme,
            'user_primary': user_primary,
            'api_billing_enabled': self.api_billing_enabled,
            'settings_input_video_fps': self.settings_input_video_fps,
            'is_public': self.is_public,
            'directory_list': self.get_with_cache(
                cache_key = 'directory_list',
                cache_miss_function = self.regenerate_directory_list_cache,
                session = session),
            'member_list': self.get_with_cache(
                cache_key = 'member_list',
                cache_miss_function = self.regenerate_member_list_cache,
                session = session),
            'preview_file_list': self.get_with_cache(
                cache_key = 'preview_file_list',
                cache_miss_function = self.regenerate_preview_file_list,
                session = session),
            'time_created': time_created,
            'default_report_dashboard_id': self.default_report_dashboard_id
        }
        return project

    def serialize_branch_list(self):

        branch_list = []
        for branch in self.branch_list:
            branch_list.append(branch.serialize())

        return branch_list

    # TODO why is this called serialize_public?
    # Was supposed to be relation to "public" as privacy setting but isn't clear
    def serialize_public(self, session):

        user_primary = None
        if self.user_primary:
            user_primary = self.user_primary.serialize_username_only()

        return {
            'name': self.name,
            'star_count': self.star_count,
            'images_count': True,  # TODO Get right stats...
            'labels_count': True,
            'project_string_id': self.project_string_id,
            'readme': self.readme,
            'user_primary': user_primary,
            'is_public': self.is_public,
            'directory_list': self.get_with_cache(
                cache_key = 'directory_list',
                cache_miss_function = self.regenerate_directory_list_cache,
                session = session),
            'api_billing_enabled': self.api_billing_enabled  # TODO review this
        }

    def get_global_attributes(self, session, schema_id = None):

        global_attribute_group_list = Attribute_Template_Group.list(
            session = session,
            group_id = None,
            project_id = self.id,
            archived = False,
            is_global = True,
            schema_id = schema_id
        )
        global_attribute_groups_serialized_list = []

        for attribute_group in global_attribute_group_list:
            global_attribute_groups_serialized_list.append(
                attribute_group.serialize_with_attributes(session = session))

        return global_attribute_groups_serialized_list

    def get_attributes(self, session, schema_id = None):

        attribute_group_list = Attribute_Template_Group.list(
            session = session,
            group_id = None,
            project_id = self.id,
            archived = False,
            is_global = None,
            schema_id = schema_id
        )

        attribute_groups_serialized_list = []

        for attribute_group in attribute_group_list:
            attribute_groups_serialized_list.append(
                attribute_group.serialize_with_attributes_and_labels(session = session))

        return attribute_groups_serialized_list

    def get_default_schema(self, session):
        return LabelSchema.get_default(session = session, project_id = self.id)

    def get_label_list(self, session, directory, schema_id = None):
        working_dir_sub_query = session.query(WorkingDirFileLink).filter(
            WorkingDirFileLink.working_dir_id == directory.id,
            WorkingDirFileLink.type == "label").subquery('working_dir_sub_query')

        # Caution, don't do "state != "removed" here,
        # Since we may have removed label files
        # With active instances, and still need this for colour map

        working_dir_file_list_query = session.query(File).filter(
            File.id == working_dir_sub_query.c.file_id)

        if schema_id is not None:
            schema = LabelSchema.get_by_id(session = session, id = schema_id, project_id = self.id)
            link_file_id_list = schema.get_label_files(session = session, ids_only = True)
            working_dir_file_list_query = working_dir_file_list_query.filter(
                File.id.in_(link_file_id_list)
            )
        t1 = time.time()
        working_dir_file_list = working_dir_file_list_query.all()
        labels_out = []

        colour_map = directory.label_file_colour_map
        rebuild_colour_map = False

        if not colour_map:
            rebuild_colour_map = True

        if rebuild_colour_map is True:
            colour_map = {}

        file_id_list = [f.id for f in working_dir_file_list]
        # Fetch Labels Data
        label_ids = [file.label_id for file in working_dir_file_list]
        labels = session.query(Label).filter(
            Label.id.in_(label_ids)
        )
        labels_serialized_dict = {}
        for label in labels:
            labels_serialized_dict[label.id] = label.serialize()
        # Fetch Attributes
        group_relations = Attribute_Template_Group.get_group_relations_list(session = session,
                                                                            file_id_list = file_id_list)

        group_rel_ids = [rel.attribute_template_group_id for rel in group_relations]
        attribute_groups_serialized_dict = {}
        # for rel in group_relations:
        #     if not attribute_groups_serialized_dict.get(rel.file_id):
        #         attribute_groups_serialized_dict[rel.file_id] = [rel.attribute_template_group.serialize_with_attributes(session = session)]
        #     else:
        #         attribute_groups_serialized_dict[rel.file_id].append(rel.attribute_template_group.serialize_with_attributes(session = session))

        # In context of a Label File!!
        for file in working_dir_file_list:

            if file.state != "removed":
                serialized_file_data = file.serialize_base_file()
                serialized_file_data['colour'] = file.colour
                serialized_file_data['label'] = labels_serialized_dict.get(file.label_id)
                serialized_file_data['attribute_group_list'] = attribute_groups_serialized_dict.get(file.id)

                labels_out.append(file.serialize_with_label_and_colour(
                    session = session))

            if rebuild_colour_map is True:
                colour_map[file.id] = file.colour
                directory.label_file_colour_map = colour_map

        if rebuild_colour_map is True:
            directory.label_file_colour_map = colour_map
            session.add(directory)

        return labels_out

    def serialize_for_export(self):
        # Just basic information for now till we review / look at other stats thing here

        return {
            'name': self.name,
            'project_string_id': self.project_string_id
        }

    def gen_initial_dir_list(self):

        if not self.directory_list:
            return None
        # Limiting to a max of 100 dirs. This code should be eventually removed from the project.
        # The correct way should be calling the dir/list endpoint and use pagination.
        limit = 100
        directory_list = []
        for directory in self.directory_list[0:limit]:

            # TODO better to do in SQL
            if directory.archived is True:
                continue

            directory_list.append(directory.serialize())

        return directory_list

    def serialize_star_list_PUBLIC(self):

        user_list = []
        for star in self.star_list:
            user_list.append(star.user.serialize_for_activity())

        return user_list

    def serialize_tag_list_PUBLIC(self):

        tag_list = []
        for tag in self.tag_list:
            tag_list.append(tag.name)

        return tag_list

    def get_project(session, project_string_id: str):
        return session.query(Project).filter(
            Project.project_string_id == project_string_id).first()

    @staticmethod
    def get_by_string_id(session, project_string_id: str):
        return session.query(Project).filter(
            Project.project_string_id == project_string_id).first()

    @staticmethod
    def get_by_id(session, id: int):
        return session.query(Project).filter(
            Project.id == id).first()

    @staticmethod
    def get(session, project_string_id):
        """
        Get using project_string
        """
        return session.query(Project).filter(
            Project.project_string_id == project_string_id).first()

    @staticmethod
    def get_users_current_project(session):
        user = session.query(User).filter_by(id = getUserID(session = session)).first()
        return session.query(Project).filter_by(id = user.current_project_string_id).first()

    @staticmethod
    def list_from_plan(
        session,
        plan
    ):
        """

        What other criteria do we need here?
        ie that project is active etc

        """
        query = session.query(Project)

        query = query.filter(
            Project.plan_id == plan.id)

        return query.all()


class Project_settings(Base):
    __tablename__ = 'project_settings'
    id = Column(Integer, primary_key = True)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", back_populates = "settings")

    # fan is faster annotations net
    # This is just project level stuff
    # Other settings in ai and ai.ml
    fan_on = Column(Boolean, default = True)
    fan_trigger_interval = Column(Integer, default = 30)
    fan_inference_size = Column(Integer, default = 90)
    fan_type = Column(String(), default = "box")
    fan_inference_minimum = Column(Float, default = .50)

    fan_method = Column(String())
    fan_sub_method = Column(String())

    """
    verify_level = Column(String())
    done_draw_level = Column(String())
    auto_save_machine_ones = Column(String())

    # Do machine made annotations auto convert at save?
    """

    def serialize(self):
        settings = {
            'fan_on': self.fan_on,
            'fan_trigger_interval': self.fan_trigger_interval,
            'fan_inference_size': self.fan_inference_size,
            'fan_type': self.fan_type,
            'fan_inference_minimum': self.fan_inference_minimum,
            'fan_method': self.fan_method,
            'fan_sub_method': self.fan_sub_method
        }
        return settings


class ProjectTag(Base):
    __tablename__ = 'project_tag'

    project_id = Column(Integer, ForeignKey('project.id'), primary_key = True)
    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key = True)

    # bidirectional collection of "project"/"ai_tags"
    project = relationship("Project", backref = backref("project_tag_junction",
                                                        cascade = "all, delete-orphan"))
    # reference to "tag" object
    tag = relationship("Tag")

    def __init__(self, tag = None, project = None, special_key = None):
        self.project = project
        self.tag = tag


class ProjectStar(Base):
    """

    """

    __tablename__ = 'project_star'

    id = Column(Integer, primary_key = True)
    created_time = Column(DateTime, default = datetime.datetime.utcnow)

    user_id = Column(Integer, ForeignKey('userbase.id'))
    user = relationship("User", foreign_keys = [user_id])

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", back_populates = "star_list",
                           foreign_keys = project_id)


class ProjectValidPermissions(Enum):
    project_create_billing_account = 'project_create_billing_account'
    project_list_inputs = 'project_list_inputs'
    project_job_list = 'project_job_list'
    project_delete = 'project_delete'
    project_edit = 'project_edit'
    project_invite_members = 'project_invite_members'
    project_list_datasets = 'project_list_datasets'
    project_view_all_datasets = 'project_view_all_datasets'
