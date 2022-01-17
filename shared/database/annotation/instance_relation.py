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

    from_instance_id =  Column(Integer, ForeignKey('instance.id'))
    from_instance = relationship("Instance", foreign_keys = [from_instance_id])

    to_instance_id =  Column(Integer, ForeignKey('instance.id'))
    to_instance = relationship("Instance", foreign_keys = [to_instance_id])

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    def serialize(self):

        return {
            'id': self.id,
            'created_time': self.time_created,
            'last_updated_time': self.time_updated,
            'type': self.type,
            'from_instance_id': self.from_instance_id,
            'to_instance_id': self.to_instance_id,
            'member_created_id': self.member_created_id,

        }

