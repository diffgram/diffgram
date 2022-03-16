# OPENCORE - ADD
from shared.database.common import *
from sqlalchemy_serializer import SerializerMixin
from shared.regular import regular_log
from sqlalchemy.dialects.postgresql import JSONB

class ProjectMigration(Base, SerializerMixin):
    __tablename__ = 'project_migration'

    id = Column(Integer, primary_key = True)
    created_time = Column(DateTime, default = datetime.datetime.utcnow)

    time_completed = Column(DateTime)

    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    time_last_attempted = Column(DateTime)

    type = Column(String())  # ["from_url", "from_video_split"]

    status = Column(String(), default = "in_progress")

    percent_complete = Column(Float, default = 0.0)

    description = Column(String())

    external_mapping_project_id = Column(Integer, ForeignKey('external_map.id'))
    external_mapping_project = relationship("ExternalMap", foreign_keys = [external_mapping_project_id])

    connection_id = Column(Integer, ForeignKey('connection_base.id'))
    connection = relationship("Connection", foreign_keys = [connection_id])

    error_log = Column(MutableDict.as_mutable(JSONB))

    retry_count = Column(Integer, default = 0)

    import_schema = Column(Boolean, default = True)
    import_files = Column(Boolean, default = False)

    # context of say a video file
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", foreign_keys = [project_id])

    migration_log = Column(MutableDict.as_mutable(JSONB), default = regular_log.default())

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    @staticmethod
    def new(
        session,
        project_id = None,
        connection_id = None,
        type = None,
        status = None,
        percent_complete = None,
        import_schema = True,
        import_files = False,
        description = None,
        external_mapping_project_id = None,
        retry_count = None,
        member_created_id = None,
        add_to_session = True,
        flush_session = True
    ):
        """
            Creates a new project migration object to track progress of a project migration from an external source.
        :param session:
        :param project_id:
        :param type:
        :param status:
        :param percent_complete:
        :param description:
        :param external_mapping_project_id:
        :param retry_count:
        :param member_created_id:
        :return:
        """

        project_migration = ProjectMigration(
            project_id = project_id,
            connection_id = connection_id,
            type = type,
            status = status,
            percent_complete = percent_complete,
            import_schema = import_schema,
            import_files = import_files,
            description = description,
            external_mapping_project_id = external_mapping_project_id,
            retry_count = retry_count,
            member_created_id = member_created_id,
        )
        if add_to_session:
            session.add(project_migration)
        if flush_session:
            session.flush()

        return project_migration

    @staticmethod
    def get_by_id(
        session,
        id: int):
        query = session.query(ProjectMigration).filter(ProjectMigration.id == id)

        return query.first()

    def serialize(self):
        data = self.to_dict(rules = (
            '-member_created',
            '-member_updated',
            '-project',
            '-connection',
            '-external_mapping_project'))

        return data
