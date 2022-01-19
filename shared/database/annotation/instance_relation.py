# OPENCORE - ADD
from shared.database.common import *
import shared.data_tools_core as data_tools_core
import hashlib
import json
from sqlalchemy.schema import Index
from shared.database.model.model import Model
from shared.database.model.model_run import ModelRun
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


class InstanceRelation(Base):
    """
        Stores a relation between 2 instances.
        Useful for relating text instances, defining parent/child relations
        etc.

    """
    __tablename__ = 'instance_relation'

    id = Column(BIGINT, primary_key = True)

    type = Column(String())

    from_instance_id = Column(Integer, ForeignKey('instance.id'))
    from_instance = relationship("Instance", foreign_keys = [from_instance_id])

    to_instance_id = Column(Integer, ForeignKey('instance.id'))
    to_instance = relationship("Instance", foreign_keys = [to_instance_id])

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    @staticmethod
    def new(session,
            from_instance_id,
            to_instance_id,
            type = 'default',
            member_created_id = None,
            member_updated_id = None,
            add_to_session = True,
            flush_session = True):

        relation = InstanceRelation(
            from_instance_id = from_instance_id,
            to_instance_id = to_instance_id,
            type = type,
            member_created_id = member_created_id,
            member_updated_id = member_updated_id
        )
        if add_to_session:
            session.add(relation)
        if flush_session:
            session.flush()

        return relation

    @staticmethod
    def get_by_id(session, relation_id):
        result = session.query(InstanceRelation).filter(
            InstanceRelation.id == relation_id
        ).first()

        return result

    @staticmethod
    def update_relations_to_new_instance_version(session, id_list_to_update: dict):
        """

        :param session:
        :param id_list_to_update: List of dicts with the shape {'old_id': 'new_id'}
        :return: The updated relations objects.
        """
        old_id_list = id_list_to_update.keys()
        relations_to_update = session.query(InstanceRelation).filter(
            InstanceRelation.to_instance_id.in_(old_id_list)
        )

        for rel in relations_to_update:
            old_id = rel.to_instance_id
            rel.to_instance_id = id_list_to_update[old_id]
            session.add(rel)
        return relations_to_update

    def serialize(self):

        return {
            'id': self.id,
            'time_created': self.time_created.strftime('%Y-%m-%d') if self.time_created else None,
            'time_updated': self.time_updated.strftime('%Y-%m-%d') if self.time_updated else None,
            'type': self.type,
            'from_instance_id': self.from_instance_id,
            'to_instance_id': self.to_instance_id,
            'member_created_id': self.member_created_id,

        }
