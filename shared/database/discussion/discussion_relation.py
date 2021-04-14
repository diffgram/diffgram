# OPENCORE - ADD
from shared.database.common import *
from shared.database.annotation.instance import Instance

class DiscussionRelation(Base):
    """


    """
    __tablename__ = 'discussion_relation'

    id = Column(Integer, primary_key = True)
    created_time = Column(DateTime, default = datetime.datetime.utcnow)

    discussion_id = Column(Integer, ForeignKey('discussion.id'))
    issue = relationship("Discussion", foreign_keys = [discussion_id])

    instance_id = Column(Integer, ForeignKey('instance.id'))
    instance = relationship("Instance", foreign_keys = [instance_id])

    file_id = Column(Integer, ForeignKey('file.id'))
    file = relationship("File", foreign_keys = [file_id])

    job_id = Column(Integer, ForeignKey('job.id'))
    job = relationship("Job", foreign_keys = [job_id])

    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", foreign_keys = [task_id])

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", foreign_keys = [project_id])

    type = Column(String, nullable = True)

    #TODO ADD PROJECT_ID
    # todo updating time, updated member,


    @staticmethod
    def new(session,
            discussion_id = None,
            instance_id = None,
            file_id = None,
            job_id = None,
            project_id = None,
            task_id = None,
            type = None,
            add_to_session = True,
            flush_session = True):

        relation = DiscussionRelation(
            discussion_id = discussion_id,
            instance_id = instance_id,
            project_id = project_id,
            file_id = file_id,
            type = type,
            job_id = job_id,
            task_id = task_id,
        )

        if add_to_session:
            session.add(relation)
        if flush_session:
            session.flush()

        return relation

    def serialize(self, session):
        relation_type = None
        instance_data = None
        if self.instance_id is not None:
            relation_type = 'instance'
            instance_data = self.instance.serialize_with_label()
        if self.file_id is not None:
            relation_type = 'file'
        if self.task_id is not None:
            relation_type = 'task'
        if self.job_id is not None:
            relation_type = 'job'
        if self.project_id is not None:
            relation_type = 'project'
        return {
            'type': relation_type,
            'discussion_id': self.discussion_id,
            'instance': instance_data,
            'file_id': self.file_id,
            'instance_id': self.instance_id,
            'task_id': self.task_id,
            'job_id': self.job_id,
            'project_id': self.project_id,
            'created_time': self.created_time,
            'id': self.id,
        }
