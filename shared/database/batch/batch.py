# OPENCORE - ADD
from shared.database.common import *
from shared.database.input import Input


class InputBatch(Base):
    __tablename__ = 'input_batch'

    """
        
    """

    id = Column(Integer, primary_key = True)

    status = Column(String, default = 'pending')
    percent_complete = Column(Float, default=0.0)

    # Assumes all inputs in batch have same directory information
    directory_id = Column(Integer, ForeignKey('working_dir.id'))    # target directory
    directory = relationship("WorkingDir", foreign_keys=[directory_id])

    source_directory_id = Column(Integer, ForeignKey('working_dir.id'))     # For internal only
    source_directory = relationship("WorkingDir", foreign_keys=[source_directory_id])

    project_id = Column(Integer, ForeignKey('project.id'), nullable = False)
    project = relationship("Project", foreign_keys = [project_id])

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    time_completed = Column(DateTime, default = datetime.datetime.utcnow)

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    @staticmethod
    def new(session,
            status = None,
            project_id = None,
            member_created_id = None,
            memeber_updated_id = None,
            add_to_session = True,
            flush_session = True):

        batch = InputBatch(
            status = status,
            project_id = project_id,
            member_created_id = member_created_id,
            member_updated_id = memeber_updated_id,
        )

        if add_to_session:
            session.add(batch)
        if flush_session:
            session.flush()

        return batch

    def check_for_completion_and_complete(self, session):
        pending_inputs = session.query(Input).filter(
            Input.status != 'success',
            Input.batch_id == self.id
        ).all()
        if len(pending_inputs) == 0:
            self.status = 'complete'
            self.time_completed = datetime.datetime.utcnow()
            session.add(self)
