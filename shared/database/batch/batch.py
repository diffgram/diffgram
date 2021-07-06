# OPENCORE - ADD
from shared.database.common import *
from shared.database.input import Input
from shared.data_tools_core import Data_tools

class InputBatch(Base):
    __tablename__ = 'input_batch'

    """
        
    """

    id = Column(Integer, primary_key = True)

    status = Column(String, default = 'pending')
    percent_complete = Column(Float, default = 0.0)

    # Assumes all inputs in batch have same directory information
    directory_id = Column(Integer, ForeignKey('working_dir.id'))  # target directory
    directory = relationship("WorkingDir", foreign_keys = [directory_id])

    # For temp storage of huge JSON pre labeled data.
    data_temp_dir = Column(String)
    # For AWS S3 Uploads
    upload_aws_id = Column(String())
    upload_aws_parts_list = Column(MutableDict.as_mutable(JSONEncodedDict))
    # For Azure Uploads
    upload_azure_block_list = Column(MutableDict.as_mutable(JSONEncodedDict))

    source_directory_id = Column(Integer, ForeignKey('working_dir.id'))  # For internal only
    source_directory = relationship("WorkingDir", foreign_keys = [source_directory_id])

    project_id = Column(Integer, ForeignKey('project.id'), nullable = False)
    project = relationship("Project", foreign_keys = [project_id])

    pre_labeled_data = Column(MutableDict.as_mutable(JSONEncodedDict))

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
            pre_labeled_data = None,
            add_to_session = True,
            flush_session = True):

        batch = InputBatch(
            status = status,
            project_id = project_id,
            member_created_id = member_created_id,
            member_updated_id = memeber_updated_id,
            pre_labeled_data = pre_labeled_data,
        )

        if add_to_session:
            session.add(batch)
        if flush_session:
            session.flush()

        return batch

    def get_pre_labeled_data_cloud_url(self):
        data_tools = Data_tools().data_tools
        url = data_tools.build_secure_url(self.data_temp_dir)
        return url


    def serialize(self):

        return {
            'id': self.id,
            'status': self.status,
            'directory_id': self.directory_id,
            'project_id': self.project_id,
            'source_directory_id': self.source_directory_id,
            'member_created_id': self.member_created_id,
            'member_updated_id': self.member_updated_id,
            'time_completed': self.time_completed,
            'time_created': self.time_created,
            'time_updated': self.time_updated,
        }

    def check_for_completion_and_complete(self, session):
        pending_inputs = session.query(Input).filter(
            Input.status != 'success',
            Input.batch_id == self.id
        ).all()
        if len(pending_inputs) == 0:
            self.status = 'complete'
            self.time_completed = datetime.datetime.utcnow()
            session.add(self)

    @staticmethod
    def get_by_id(session, id):
        result = session.query(InputBatch).filter(InputBatch.id == id).first()
        return result
