# OPENCORE - ADD
from shared.database.common import *


class Project_Directory_List(Base):
    __tablename__ = 'project_directory_list'

    """

    Not sure if name is right, could be 
    project_directory_map or project_to_directory

    """

    working_dir_id = Column(Integer, ForeignKey('working_dir.id'), primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'), primary_key=True)

    directory = relationship("WorkingDir")

    # cache of nickname, canoncial on directory itself
    nickname = Column(String())  # Implies user selectable, real id is primary keys

    archived = Column(Boolean)

    project = relationship("Project")

    created_time = Column(DateTime, default=datetime.datetime.utcnow)
    last_time = Column(DateTime, onupdate=datetime.datetime.utcnow)

    def get_by_project(
            session,
            project_id,
            exclude_archived=True,
            kind="counts",
            directory_ids_to_ignore_list: list = None,
            nickname: str = None
    ):
        """
        Get counts or objects of class Project_Directory_List

        object.working_dir_id or object.project_id is available
        object.directory  (is working_dir_id while undergoing rename)

        archived is a cached value? source of truth should be on directory
        itself?

        """

        query = session.query(Project_Directory_List).filter(
            Project_Directory_List.project_id == project_id)

        if nickname:
            query = query.filter(
                Project_Directory_List.nickname == nickname)

        if directory_ids_to_ignore_list is not None:
            query = query.filter(
                Project_Directory_List.working_dir_id.notin_(
                    directory_ids_to_ignore_list))

        # Some kind of bug with this
        # it was not returning anything
        # the Null default is confusing this somehow, just disable for now
        # if exclude_archived is True:
        #	query = query.filter(Project_Directory_List.archived != True)

        if kind == "counts":
            return query.count()

        if kind == "objects":
            return query.all()

    def link(session,
             working_dir_id,
             project_id):
        """
        Get a single link based on working dir and project

        """

        link = session.query(Project_Directory_List).filter(
            Project_Directory_List.working_dir_id == working_dir_id,
            Project_Directory_List.project_id == project_id).first()

        return link

    def remove(session,
               working_dir_id,
               project_id):
        """
        Hard delete a link
        """

        link = Project_Directory_List.link(
            session,
            working_dir_id,
            project_id)

        if link:
            session.delete(link)

    @staticmethod
    def add(session,
            working_dir_id,
            project_id,
            nickname=None
            ):
        """
        Create a new link  (adds to session too)

        session,
        working_dir_id,
        project_id
        """

        link = Project_Directory_List(
            working_dir_id=working_dir_id,
            project_id=project_id,
            nickname=nickname
        )

        session.add(link)

    # CAUTION only for init with a project, not general new
    @staticmethod
    def add_default(
            session,
            working_dir_id,
            project):
        """
        Meant as a unified way to add a default directory
        since this could happen from new project, or migration
        or potentially some other issue

        The significance of a default directory is not super
        clear (beyond a project needing at least 1 directory
        to operate in a useful way)

        """

        nickname = "Default"

        session.add(project)
        project.directory_default.nickname = nickname

        Project_Directory_List.add(
            session=session,
            working_dir_id=project.directory_default_id,
            project_id=project.id,
            nickname=nickname
        )

    def serialize(self):

        # Future, could cache
        # things like file counts and other stuff here...

        return {
            'directory_id': self.working_dir_id,
            'jobs_to_sync': self.directory.jobs_to_sync,
            'project_id': self.project_id,
            'nickname': self.nickname,
            'created_time': self.created_time.isoformat()
        }
