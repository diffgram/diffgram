# OPENCORE - ADD
from shared.database.common import *
from shared.helpers.permissions import getUserID
from shared.database import hashing_functions
from shared.database.discussion.discussion_comment import DiscussionComment
from shared.database.discussion.discussion_relation import DiscussionRelation


class User(Base):
    __tablename__ = 'userbase'

    """
    
    """

    # TODO may want to get full name here

    id = Column(Integer, primary_key = True)

    member_id = Column(Integer, ForeignKey('member.id'))
    member = relationship('Member', foreign_keys = "Member.user_id", uselist = False)

    qos_last_cached_value = Column(Float)  # Quality of service, most recent

    first_name = Column(String(100))
    last_name = Column(String(100))

    occupation_list = Column((ARRAY(String)))
    linkedin_profile_url = Column(String())

    how_hear_about_us = Column(String())

    company_name = Column(String())

    security_disable_global = Column(Boolean)  # If True, Disable user login completely
    security_email_verified = Column(Boolean)  # If True, email is

    api_actions = Column(Boolean, default = False)

    api_enabled_builder_brain = Column(Boolean)
    api_enabled_builder = Column(Boolean)  # Computer vision suite
    api_enabled_trainer = Column(Boolean)  # Annotation

    # A user can have both in theory,
    # so we say last in case they change modes
    last_builder_or_trainer_mode = Column(String)  # ["builder", "trainer"]

    phone_number = Column(String)
    city = Column(String)  # Until we get proper address collection setup

    # Should a user have a generic hash we can reference them by
    # And should this be the username until the user picks one?
    username = Column(String())

    email = Column(String(100), nullable = False)  # email is key
    password_hash = Column(String())

    # TODO rename to "attempt_count" in light of magic email thing?
    password_attempt_count = Column(Integer, default = 0)

    auto_commit = Column(Boolean, default = True)

    otp_secret = Column(String())
    otp_enabled = Column(Boolean)
    otp_backup = Column(MutableDict.as_mutable(JSONEncodedDict),
                        default = {})  # code : redeemed_or_not
    otp_current_session = Column(String())
    otp_current_session_expiry = Column(Integer)

    # TODO add otp_remember_browser (/ip?) and otp_recovery?

    profile_image_id = Column(Integer, ForeignKey('image.id'))
    profile_image = relationship("Image")

    # Common image information here so we don't have to do an extra
    # query on class Image() every time we get user
    # Not sure if it's worth it to do it this way
    profile_image_url = Column(String())
    profile_image_blob = Column(String())  # blob dir
    profile_image_expiry = Column(Integer)

    profile_image_thumb_url = Column(String())
    profile_image_thumb_blob = Column(String())

    created_time = Column(DateTime, default = datetime.datetime.utcnow)

    created_remote_address = Column(String())

    last_time = Column(DateTime, onupdate = datetime.datetime.utcnow)

    current_project_string_id = Column(String(100))

    project_current_id = Column(Integer, ForeignKey("project.id"))
    project_current = relationship('Project',
                                   foreign_keys = [project_current_id],
                                   post_update = True)

    ## ##
    # Dictionary of  User + Permission?
    # ie  ai_id : 'permission_level_0'
    permissions_projects = Column(MutableDict.as_mutable(JSONEncodedDict),
                                  default = {})

    # NEW
    # permissions_diffgram_features = Column(MutableDict.as_mutable(JSONEncodedDict),
    #											default = {})
    ###

    # Permissions general is simply array vs dict for projects check
    permissions_general = Column(MutableDict.as_mutable(JSONEncodedDict),
                                 default = {
                                     'general': []
                                 })

    is_super_admin = Column(Boolean, default = False)

    # deprecated in favour of single user
    # ais = association_proxy('userbase_ais', 'ai')

    projects = association_proxy('userbase_projects', 'project')

    last_task_id = Column(Integer, ForeignKey('task.id'))
    last_task = relationship("Task", foreign_keys = [last_task_id])

    ###

    available_for_annotation_assignment = Column(Boolean, default = True)
    is_annotator = Column(Boolean, default = False)

    # migrating this to class Member()

    signup_code_id = Column(Integer, ForeignKey('signup_code.id'))
    signup_code = relationship("Signup_code", foreign_keys = [signup_code_id])

    verify_email_code_id = Column(Integer, ForeignKey('signup_code.id'))
    verify_email_code = relationship("Signup_code", foreign_keys = [verify_email_code_id])
    ###  ###

    follow_ing_count = Column(Integer, default = 0)  # ADD to db
    follow_ers_count = Column(Integer, default = 0)

    follow_ing_list = relationship("UserFollow",
                                   foreign_keys = "UserFollow.user_id")
    follow_ers_list = relationship("UserFollow",
                                   foreign_keys = "UserFollow.following_user_id")

    # See builder_signup.py
    signup_role = Column(String())  # ie [leadership, product, engineering, student, other]
    signup_demo = Column(String())  # ie [yes, sales, not_yet]
    signup_how_many_data_labelers = Column(String())

    def get_profile_image_url(self):
        if (self.profile_image_expiry is None or self.profile_image_expiry <= time.time()) and self.profile_image_blob:
            self.profile_image_url = data_tools.build_secure_url(blob_name = self.profile_image_blob)
            self.profile_image_thumb_url = data_tools.build_secure_url(blob_name = self.profile_image_thumb_blob)
        return self.profile_image_url

    def get_profile_image_thumb_url(self):
        if (self.profile_image_expiry is None or self.profile_image_expiry <= time.time()) and self.profile_image_blob:
            self.profile_image_url = data_tools.build_secure_url(blob_name = self.profile_image_blob)
            self.profile_image_thumb_url = data_tools.build_secure_url(blob_name = self.profile_image_thumb_blob)
        return self.profile_image_thumb_url

    def serialize(self):

        project_current = None
        if self.project_current:
            project_current = self.project_current.serialize()

        return {
            'id': self.id,
            'current_project_string_id': self.current_project_string_id,
            'is_super_admin': self.is_super_admin,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile_image_url': self.get_profile_image_url(),
            'profile_image_thumb_url': self.get_profile_image_thumb_url(),
            'username': self.username,
            'follow_ing_count': self.follow_ing_count,
            'follow_ers_count': self.follow_ers_count,
            'otp_enabled': self.otp_enabled,
            'email': self.email,
            'last_builder_or_trainer_mode': self.last_builder_or_trainer_mode,
            'trainer': {
                'show_first_time_message': True
            },
            'project_current': project_current,
            'api': {
                'api_enabled_trainer': self.api_enabled_trainer,
                'api_enabled_builder': self.api_enabled_builder,
                'api_actions': self.api_actions
            },
            'security_email_verified': self.security_email_verified

        }

    def serialize_for_activity(self):
        # Careful, this may be accessed by other users (ie on same project)

        user = {
            'id': self.id,
            'first_name': self.first_name,
            'id': self.id,
            'last_name': self.last_name,
            'profile_image_thumb_url': self.get_profile_image_thumb_url(),
            'username': self.username
        }
        return user

    def serialize_with_permission(self, project_string_id):

        permission_level = None
        if self.permissions_projects:
            permission_level = self.permissions_projects.get(project_string_id)

        return {
            'id': self.id,
            'member_id': self.member_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile_image_thumb_url': self.get_profile_image_thumb_url(),
            'username': self.username,
            'permission_level': permission_level,
            'member_kind': 'human'
        }
    

    def serialize_with_permission_only(self, project_string_id):
        return self.permissions_projects.get(project_string_id, None)

    def serialize_username_only(self):
        return {
            'username': self.username
        }

    def serialize_public(self, session):
        # Careful, **PUBLIC** info
        project_list = []
        for project in self.projects:
            if project.is_public is True:
                project_list.append(project.serialize_public(session))

        user = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile_image_url': self.profile_image_url,
            'project_list': project_list
        }
        return user

    def build_followers_list(self):
        user_list = []
        for user_follow in self.follow_ers_list:
            user_list.append(user_follow.user.serialize_for_activity())
        return user_list

    def build_following_list(self):
        user_list = []
        for user_follow in self.follow_ing_list:
            user_list.append(user_follow.following_user.serialize_for_activity())
        return user_list

    def serialize_follow_ers_list_PUBLIC(self):
        return {
            'user_list': self.build_followers_list()
        }

    def serialize_follow_ing_list_PUBLIC(self):
        return {
            'user_list': self.build_following_list()
        }

    def get_by_username(session, username_string):

        return session.query(User).filter(User.username == username_string).first()

    def get_current_user(session):

        return session.query(User).filter_by(id = getUserID()).first()

    def get(session):

        return session.query(User).filter_by(id = getUserID()).first()

    def get_by_member_id(
        session,
        member_id: int
    ):

        return session.query(User).filter(
            User.member_id == member_id).first()

    def get_by_id(session,
                  user_id):

        return session.query(User).filter(
            User.id == user_id).first()

    def get_by_email(session,
                     email):

        return session.query(User).filter(User.email == email).first()


setattr(User, "getUserID", getUserID)


# TODO rename to Auth_code to support verify, reset, etc.
class Signup_code(Base):
    """

    """
    __tablename__ = 'signup_code'
    id = Column(Integer, primary_key = True)

    type = Column(String())
    # ['verify_signup', 'invite_by_trainer_org']

    created_time_int = Column(Integer)  # integer time vs datetime...

    # TODO link to user directly when possible?

    created_time = Column(DateTime, default = datetime.datetime.utcnow)
    redeemed_time = Column(DateTime)

    code = Column(String(100))
    is_available = Column(Boolean, default = True)

    email_sent_to = Column(String(100))
    project_string_id = Column(String(100))
    permission_level = Column(String())

    # TODO this is awkward here
    # Why not part of init?
    # Also maybe rename to "hash" ? is code confusing?
    def new_code(self, session):
        salt = hashing_functions.make_salt()
        seed = "2uji9890"
        self.code = hashing_functions.hashlib.sha256(
            (self.email_sent_to + seed + salt).encode('utf-8')).hexdigest()
        return self.code

    @staticmethod
    def get_latest_code(session, email):
        code = session.query(Signup_code).filter(
            Signup_code.email_sent_to == email,
            Signup_code.is_available == True
        ).first()
        return code


class UserbaseProject(Base):
    """
    each user has a working directory per project
    a "working directory" is a version that is unique
    to the user and to the project
    the version gets attached to the project, and this

    So for example
    userbase_project =
        query(UserbaseProject).filter(
            UserbaseProject.user_id == user_id,
            UserbaseProject.project_id == project_id).one()
    userbase_project.working_dir == working dir version for
        that user and for that project

    """
    __tablename__ = 'userbase_project'

    user_id = Column(Integer, ForeignKey('userbase.id'), primary_key = True)
    project_id = Column(Integer, ForeignKey('project.id'), primary_key = True)

    working_dir_id = Column(Integer, ForeignKey('working_dir.id'))
    working_dir = relationship('WorkingDir')

    created_time = Column(DateTime, default = datetime.datetime.utcnow)
    last_time = Column(DateTime, onupdate = datetime.datetime.utcnow)

    # bidirectional collection of "user"/"user_projects"
    userbase = relationship("User", backref = backref("userbase_projects",
                                                      cascade = "all, delete-orphan"))

    project = relationship("Project", backref = backref("userbase_projects",
                                                        cascade = "all, delete-orphan"))  # Should be exact match for class

    # TODO clarify this is the working dir we have "set"
    # therefore don't need branch?
    def get_working_dir(session, user_id, project_id):
        userbase_project = session.query(UserbaseProject).filter(
            UserbaseProject.user_id == user_id,
            UserbaseProject.project_id == project_id).first()

        # TODO this is a kinda "ugly" work around...
        # TODO need to check security impllications of this
        if userbase_project is None:
            project = session.query(Project).filter(Project.id == project_id).first()
            return project.directory_default

        return userbase_project.working_dir

    def set_working_dir(session,
                        user_id,
                        project_id,
                        working_dir_id):
        userbase_project = session.query(UserbaseProject).filter(
            UserbaseProject.user_id == user_id,
            UserbaseProject.project_id == project_id).one()

        userbase_project.working_dir_id = working_dir_id
        session.add(userbase_project)

    def __init__(self, project = None, userbase = None):
        self.userbase = userbase
        self.project = project


class UserFollow(Base):
    """

    """

    __tablename__ = 'user_follow'

    id = Column(Integer, primary_key = True)
    created_time = Column(DateTime, default = datetime.datetime.utcnow)

    user_id = Column(Integer, ForeignKey('userbase.id'))
    user = relationship("User",
                        foreign_keys = [user_id])

    following_user_id = Column(Integer, ForeignKey('userbase.id'))
    following_user = relationship("User",
                                  foreign_keys = following_user_id)


class UserLoginHistory(Base):
    __tablename__ = 'user_login_history'

    """
    
    """

    # TODO may want to get full name here

    id = Column(Integer, primary_key = True)

    created_time = Column(DateTime, default = datetime.datetime.utcnow)

    success = Column(Boolean)
    otp_success = Column(Boolean)

    remote_address = Column(String())

    user_id = Column(Integer, ForeignKey('userbase.id'))
    user = relationship("User")


def new_login_history(session, success, otp_success, remote_address, user_id):
    user_login_history = UserLoginHistory()
    session.add(user_login_history)

    user_login_history.success = success
    user_login_history.otp_success = otp_success
    user_login_history.remote_address = remote_address
    user_login_history.user_id = user_id


setattr(User, "new_login_history", new_login_history)
