# OPENCORE - ADD
from shared.database.common import *
from shared.database.discussion.discussion_member import DiscussionMember
import shared.database.discussion.discussion_relation as discussion_relation_models
from shared.database.annotation.instance import Instance
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


class Model(Base):
    """


    """
    __tablename__ = 'model'

    id = Column(Integer, primary_key = True)

    created_time = Column(DateTime, default = datetime.datetime.utcnow)
    last_updated_time = Column(DateTime, onupdate = datetime.datetime.utcnow)
    deleted_time = Column(DateTime, nullable = True)

    reference_id = Column(String())

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_created_id])

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", foreign_keys=[project_id])

    @staticmethod
    def get_by_id(session, id):
        model_run = session.query(Model).filter(Model.id == id).first()
        return model_run

    @staticmethod
    def get_by_reference_id(session, reference_id):
        model_run = session.query(Model).filter(Model.reference_id == reference_id).first()
        return model_run

    @staticmethod
    def new(session,
            reference_id: str = None,
            project_id: int = None,
            member_created_id: int = None,
            add_to_session: bool = True,
            flush_session: bool = True):
        model = Model(
            reference_id = reference_id,
            member_created_id = member_created_id,
            project_id = project_id,
        )
        if add_to_session:
            session.add(model)
        if flush_session:
            session.flush()
        return model

    @staticmethod
    def list(session,
             project_id: int = None,
             ends: str = None,
             starts: str = None,
             ):

        if project_id is None:
            return

        query = session.query(Model).filter(Model.project_id == project_id)

        if starts:
            query = query.filter(Model.created_time >= starts)

        if ends:
            query = query.filter(Model.created_time <= ends)

        query = query.order_by(Model.created_time)

        model_list = query.all()

        return model_list
