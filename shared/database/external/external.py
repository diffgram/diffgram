# OPENCORE - ADD
from shared.database.common import *
import analytics
from shared.database.input import Input
from shared.database.auth.member import Member
from shared.database.source_control.file import File
import collections


class ExternalMap(Base):
    __tablename__ = 'external_map'

    """
    
    """

    id = Column(BIGINT, primary_key=True)

    external_id = Column(String())  # Literal external id, eg "jlksa22kljk2221232"
    # or 'user@gmail.com', "185765", etc.

    type = Column(String())  # 'scale' 'labelbox', 'custom' etc... could have subtypes with _
    diffgram_class_string = Column(String())  # 'project'
    # can cache this for easier lookups eg diffgram_class_string + external_id

    url = Column(String())  # Cache direct link to external resource if available

    # Relates to these Diffgram ids:
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", foreign_keys=[project_id])

    job_id = Column(Integer, ForeignKey('job.id'))
    job = relationship("Job", foreign_keys=[job_id])

    file_id = Column(Integer, ForeignKey('file.id'))
    file = relationship("File", foreign_keys=[file_id])

    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", foreign_keys=[task_id])

    instance_id = Column(Integer, ForeignKey('instance.id'))
    instance = relationship("Instance", foreign_keys=[instance_id])

    attribute_template_group_id = Column(Integer, ForeignKey('attribute_template_group.id'))
    attribute_template_group = relationship("Attribute_Template_Group", foreign_keys=[attribute_template_group_id])

    user_id = Column(Integer, ForeignKey('userbase.id'))
    user = relationship("User", foreign_keys=[user_id])

    connection_id = Column(Integer, ForeignKey('connection_base.id'))
    connection = relationship("Connection", foreign_keys=[connection_id])

    dataset_id = Column(Integer, ForeignKey('working_dir.id'))
    dataset = relationship("WorkingDir",
                           foreign_keys=[dataset_id])
    ### End external to internal map object relations

    # Internal tracking objects for this class
    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys=[member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys=[member_updated_id])

    time_created = Column(DateTime, default=datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)

    def serialize(self):

        return {
            'external_id': self.external_id,
            'type': self.type,
            'diffgram_class_string': self.diffgram_class_string,
            'url': self.url,
            'project_id': self.project_id,
            'job_id': self.job_id,
            'file_id': self.file_id,
            'attribute_template_group_id': self.attribute_template_group_id,
            'user_id': self.user_id,
            'connection_id': self.connection_id,
            'dataset_id': self.dataset_id,
            'member_created_id': self.member_created_id,
            'member_updated_id': self.member_updated_id,
        }

    @staticmethod
    def new(session,
            external_id,
            diffgram_class_string: str = None,
            type=None,
            url=None,
            project=None,
            job=None,
            file=None,
            task=None,
            attribute_template_group=None,
            attribute_template_group_id=None,
            file_id=None,
            user=None,
            connection=None,
            dataset=None,
            member_created=None,
            member_updated=None,
            add_to_session=False,
            flush_session=False
            ):
        """
        """
        if file_id is not None:
            file = File.get_by_id(session, file_id=file_id)
            session.add(file)
        external_map = ExternalMap(
            type=type,
            external_id=external_id,
            diffgram_class_string=diffgram_class_string,
            url=url,
            project=project,
            job=job,
            file=file,
            task=task,
            user=user,
            attribute_template_group_id=attribute_template_group_id,
            attribute_template_group=attribute_template_group,
            dataset=dataset,
            connection=connection,
            member_created=member_created,
            member_updated=member_updated
        )
        if add_to_session is True:
            session.add(external_map)

        if flush_session is True:
            session.flush()
        return external_map

    @staticmethod
    def get(session,
            external_id=None,
            connection_id=None,
            job_id=None,
            task_id=None,
            file_id=None,
            diffgram_class_string: str = None,
            type: str = None,
            limit=100,
            return_kind="first",  # [first, all, count]
            date_to=None,
            date_from=None
            ):
        """
        """
        query = session.query(ExternalMap)

        if external_id:
            query = query.filter(ExternalMap.external_id == external_id)

        if connection_id:
            query = query.filter(ExternalMap.connection_id == connection_id)

        if job_id:
            query = query.filter(ExternalMap.job_id == job_id)

        if task_id:
            query = query.filter(ExternalMap.task_id == task_id)

        if file_id:
            if isinstance(file_id, collections.Iterable):
                query = query.filter(ExternalMap.file_id.in_(file_id))
            else:
                query = query.filter(ExternalMap.file_id == file_id)
        if diffgram_class_string:
            query = query.filter(ExternalMap.diffgram_class_string == diffgram_class_string)

        if type:
            query = query.filter(ExternalMap.type == type)

        # TODO would like from this point on to be more abstract mixin, since it's used often
        if date_to or date_from:
            datetime_property = ExternalMap.time_created

            if date_from and date_to:
                query = query.filter(
                    datetime_property >= date_from,
                    datetime_property <= date_to)
            else:
                if date_from:
                    query = query.filter(datetime_property >= date_from)

                if date_to:
                    query = query.filter(datetime_property <= date_to)

        if limit:
            query = query.limit(limit)

        if return_kind == "count":
            return query.count()

        if return_kind == "all":
            return query.all()

        if return_kind == "first":
            return query.first()
