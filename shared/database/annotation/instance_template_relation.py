# OPENCORE - ADD
from shared.database.common import *
import shared.data_tools_core as data_tools_core
import hashlib
import json


class InstanceTemplateRelation(Base):
    """
    An template for an instance.

    """
    __tablename__ = 'instance_template_relation'

    id = Column(BIGINT, primary_key = True)

    created_time = Column(DateTime, default = datetime.datetime.utcnow)
    last_updated_time = Column(DateTime, onupdate = datetime.datetime.utcnow)
    deleted_time = Column(DateTime, nullable = True)

    instance_id = Column(Integer, ForeignKey('instance.id'))
    instance = relationship("Instance")

    instance_template_id = Column(Integer, ForeignKey('instance_template.id'))
    instance_template = relationship("InstanceTemplate")
