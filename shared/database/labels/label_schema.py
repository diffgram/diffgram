from shared.database.common import *
from shared.shared_logger import get_shared_logger
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm.session import Session


class LabelSchema(Base, SerializerMixin):
    """
     Tables for grouping multiple file labels into a single entity.
     The label schema exists in the scope of a single project and can be
     applied to task templates.
    """
    __tablename__ = 'label_schema'

    id = Column(Integer, primary_key = True)

    name = Column(String(), nullable = False)

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", foreign_keys = [project_id])

    archived = Column(Boolean(), default = False)

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    @staticmethod
    def get_by_id(session: Session, id: int) -> 'LabelSchema':
        result = session.query(LabelSchema).filter(
            LabelSchema.id == id
        ).first()
        return result

    @staticmethod
    def new(session: Session, name: str, project_id: int, member_created_id: int) -> 'LabelSchema':
        schema = LabelSchema(
            name = name,
            project_id = project_id,
            member_created_id = member_created_id,
            archived = False,
        )

        session.add(schema)
        session.flush()

        return schema

    def serialize(self):
        data = self.to_dict(rules = (
            '-member_created',
            '-member_updated',
            '-project'))

        return data

    def add_label_file(self, session: Session, label_file_id: int, member_created_id: int):
        rel = LabelSchemaLink.new_label_link(
            session = session,
            schema_id = self.id,
            label_file_id = label_file_id,
            member_created_id = member_created_id
        )
        return rel

    def add_attribute_group(self, session: Session, attribute_group_id: int, member_created_id: int):
        rel = LabelSchemaLink.new_attribute_group_link(
            session = session,
            schema_id = self.id,
            attribute_group_id = attribute_group_id,
            member_created_id = member_created_id
        )
        return rel

    def add_instance_template(self, session: Session, instance_template_id: int, member_created_id: int):
        rel = LabelSchemaLink.new_instance_template_link(
            session = session,
            schema_id = self.id,
            instance_template_id = instance_template_id,
            member_created_id = member_created_id
        )
        return rel

    @staticmethod
    def list(session: Session, project_id: int):
        query = session.query(LabelSchema).filter(
            LabelSchema.project_id == project_id,
            LabelSchema.archived == False
        )
        result = query.all()
        return result

    def get_label_files(self, session: Session):
        query = session.query(LabelSchemaLink).filter(
            LabelSchemaLink.schema_id == self.id,
            LabelSchemaLink.label_file_id != None
        )
        links = query.all()
        result = []
        for elm in links:
            result.append(elm.label_file)
        return result

    def get_attribute_groups(self, session: Session):
        query = session.query(LabelSchemaLink).filter(
            LabelSchemaLink.schema_id == self.id,
            LabelSchemaLink.attribute_template_group_id != None
        )
        links = query.all()
        result = []
        for elm in links:
            result.append(elm.attribute_template_group)
        return result

    def get_instance_templates(self, session: Session):
        query = session.query(LabelSchemaLink).filter(
            LabelSchemaLink.schema_id == self.id,
            LabelSchemaLink.instance_template_id != None
        )
        links = query.all()
        result = []
        for elm in links:
            result.append(elm.instance_template)
        return result

class LabelSchemaLink(Base, SerializerMixin):
    __tablename__ = 'label_schema_link'
    id = Column(Integer, primary_key = True)

    schema_id = Column(Integer, ForeignKey('label_schema.id'))
    schema = relationship("LabelSchema", foreign_keys = [schema_id])

    instance_template_id = Column(Integer, ForeignKey('instance_template.id'))
    instance_template = relationship("InstanceTemplate", foreign_keys = [instance_template_id])

    attribute_template_group_id = Column(Integer, ForeignKey('attribute_template_group.id'))
    attribute_template_group = relationship("Attribute_Template_Group", foreign_keys = [attribute_template_group_id])

    label_file_id = Column(Integer, ForeignKey('file.id'))
    label_file = relationship("File", foreign_keys = [label_file_id])

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    @staticmethod
    def new_label_link(session: Session, schema_id: int, label_file_id: int, member_created_id: int) -> 'LabelSchemaLink':
        schema_link = LabelSchemaLink(
            schema_id = schema_id,
            label_file_id = label_file_id,
            member_created_id = member_created_id
        )

        session.add(schema_link)
        session.flush()

        return schema_link

    @staticmethod
    def new_attribute_group_link(session: Session, schema_id: int, attribute_group_id: int, member_created_id: int) -> 'LabelSchemaLink':
        schema_link = LabelSchemaLink(
            schema_id = schema_id,
            attribute_template_group_id = attribute_group_id,
            member_created_id = member_created_id
        )

        session.add(schema_link)
        session.flush()

        return schema_link

    @staticmethod
    def new_instance_template_link(session: Session, schema_id: int, instance_template_id: int, member_created_id: int) -> 'LabelSchemaLink':
        schema_link = LabelSchemaLink(
            schema_id = schema_id,
            instance_template_id = instance_template_id,
            member_created_id = member_created_id
        )

        session.add(schema_link)
        session.flush()

        return schema_link

    def serialize(self):
        data = self.to_dict(rules = (
            '-schema',
            '-label_file',
            '-member_created',
            '-member_updated'))

        return data
