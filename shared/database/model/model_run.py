# OPENCORE - ADD
from shared.database.common import *


class ModelRun:
    """


    """
    __tablename__ = 'model_run'

    id = Column(Integer, primary_key = True)

    created_time = Column(DateTime, default = datetime.datetime.utcnow)
    last_updated_time = Column(DateTime, onupdate = datetime.datetime.utcnow)
    deleted_time = Column(DateTime, nullable = True)

    reference_id = Column(String())

    model_id = Column(Integer, ForeignKey('model.id'), nullable = False)
    model = relationship("Model", foreign_keys = [model_id])

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_created_id])

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", foreign_keys = [project_id])

    @staticmethod
    def get_by_id(session, id):
        model_run = session.query(ModelRun).filter(ModelRun.id == id).first()
        return model_run

    @staticmethod
    def get_by_reference_id(session, reference_id):
        model_run = session.query(ModelRun).filter(ModelRun.reference_id == reference_id).first()
        return model_run

    @staticmethod
    def new(session,
            reference_id: str = None,
            project_id: int = None,
            member_created_id: int = None,
            model_id = None,
            add_to_session: bool = True,
            flush_session: bool = True):

        model_run = ModelRun(
            project_id = project_id,
            member_created_id = member_created_id,
            reference_id = reference_id,
            model_id = model_id,
        )
        if add_to_session:
            session.add(model_run)
        if flush_session:
            session.flush()
        return model_run

    @staticmethod
    def list(session,
             project_id: int = None,
             model_id: int = None,
             ends: str = None,
             starts: str = None,
             ):

        if project_id is None:
            return

        query = session.query(ModelRun).filter(ModelRun.project_id == project_id)

        if starts:
            query = query.filter(ModelRun.created_time >= starts)
        if model_id:
            query = query.filter(ModelRun.model_id == model_id)
        if ends:
            query = query.filter(ModelRun.created_time <= ends)

        query = query.order_by(ModelRun.created_time)

        model_list = query.all()

        return model_list
