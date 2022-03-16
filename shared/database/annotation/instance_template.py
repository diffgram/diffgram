# OPENCORE - ADD
from shared.database.common import *
from shared.database.annotation.instance_template_relation import InstanceTemplateRelation
from shared.database.annotation.instance import Instance
import shared.data_tools_core as data_tools_core
import hashlib
import json


class InstanceTemplate(Base):
    """
    An template for an instance.

    """
    __tablename__ = 'instance_template'

    id = Column(BIGINT, primary_key = True)

    name = Column(String)

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project")

    instance_relations = relationship(InstanceTemplateRelation)

    reference_width = Column(Integer)
    reference_height = Column(Integer)

    # 'active, or 'archived'
    status = Column(String(), default = 'active')

    mode = Column(String(), default = '1_click')

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_created_id])

    created_time = Column(DateTime, default = datetime.datetime.utcnow)
    last_updated_time = Column(DateTime, onupdate = datetime.datetime.utcnow)
    deleted_time = Column(DateTime, nullable = True)

    @staticmethod
    def get_by_id(session, id):
        return session.query(InstanceTemplate).filter(
            InstanceTemplate.id == id
        ).first()

    @staticmethod
    def list(
            session,
            project,
            status = 'active'
    ):
        """
            Returns the InstanceTemplates object list matching the given
            parameters.
        :param session:
        :param project:
        :return:
        """
        result = session.query(InstanceTemplate).filter(
            InstanceTemplate.project_id == project.id,
            InstanceTemplate.status == status
        ).all()

        return result

    @staticmethod
    def new(session,
            project,
            name: str,
            instance_list,
            add_to_session: bool = True,
            member_created = None,
            reference_width = None,
            mode = '1_click',
            reference_height = None,
            flush_session: bool = True):

        instance_template = InstanceTemplate(
            project_id = project.id,
            name = name,
            member_created_id = member_created.id,
            reference_height = reference_height,
            mode = mode,
            reference_width = reference_width,
        )
        if add_to_session:
            session.add(instance_template)
        if flush_session:
            session.flush()

        for instance in instance_list:
            rel = InstanceTemplateRelation(
                instance_id = instance.id,
                instance_template_id = instance_template.id
            )
            session.add(rel)

        return instance_template

    def get_instance_list(self, session):
        rels_list = session.query(InstanceTemplateRelation).filter(
            InstanceTemplateRelation.instance_template_id == self.id
        ).all()
        id_list = [rel.instance_id for rel in rels_list]
        instance_list = session.query(Instance).filter(
            Instance.id.in_(id_list)
        ).all()
        return instance_list

    def serialize(self, session):
        instance_list = self.get_instance_list(session)
        instance_list_serialized = [inst.serialize() for inst in instance_list]
        return {
            'id': self.id,
            'instance_list': instance_list_serialized,
            'mode': self.mode,
            'name': self.name,
            'project_id': self.project_id,
            'member_created_id': self.member_created_id,
            'created_time': self.created_time,
            'last_updated_time': self.last_updated_time,
            'deleted_time': self.deleted_time,
            'status': self.status,
            'reference_width': self.reference_width,
            'reference_height': self.reference_height,
        }
