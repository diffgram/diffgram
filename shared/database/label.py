# OPENCORE - ADD
from shared.database.common import *
from shared.helpers.performance import timeit

class Label(Base):
    __tablename__ = 'label'

    id = Column(Integer, primary_key = True)
    name = Column(String(200))

    soft_delete = Column(Boolean)


    @staticmethod
    @timeit
    def get_by_id(session, id):
        return session.query(Label).filter(
            Label.id == id
        ).first()

    @staticmethod
    def get_by_name(session, label_name):
        return session.query(Label).filter(
            Label.name == label_name
        ).first()

    @staticmethod
    def new(session,
            add_to_session = True,
            flush_session = True,
            name = None):

        label = session.query(Label).filter(
            Label.name == name
        ).first()

        if not label:
            label = Label(name = name)
            if add_to_session:
                session.add(label)
            if flush_session:
                session.flush()
        return label


    @timeit
    def serialize(self):
        label = {
            'id': self.id,
            'name': self.name 
        }
        return label

    def serialize_PUBLIC(self):
        return {
            'name': self.name
        }
