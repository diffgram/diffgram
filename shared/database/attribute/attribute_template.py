# OPENCORE - ADD
from shared.database.common import *


class Attribute_Template(Base):
    """

    """

    __tablename__ = 'attribute_template'
    id = Column(BIGINT, primary_key = True)

    group_id = Column(Integer, ForeignKey('attribute_template_group.id'), index = True)  # Add index
    group = relationship("Attribute_Template_Group", foreign_keys = [group_id])

    archived = Column(Boolean, default = False)  # Hide from list

    display_order = Column(Integer)  # 0 indexed, display 0 first

    name = Column(String())

    # CAUTION this a value or CHILD group in graph
    # is **NOT** 'checkbox' 'text' etc. that is at the group level.
    # TODO rename this away from 'kind' it's too confusing with other thing
    # ie "opens_nested_node" isn't quite right but at least directionally
    # more clear...
    kind = Column(String())
    value_type = Column(String())  # ie integer

    project_id = Column(Integer, ForeignKey('project.id'), index=True)
    project = relationship("Project")

    # Used for Treeview attributes.
    parent_id = Column(Integer, ForeignKey('attribute_template.id'))

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    @staticmethod
    def new(
        project,
        member,
        group,
        parent_id = None,
        name = None):
        """
        """

        if group is None:
            return False

        attribute = Attribute_Template(
            project = project,
            member_created = member,
            group = group,
            parent_id = parent_id,
            name = name
        )

        return attribute

    @staticmethod
    def get_by_name_and_parent_id(session, attr_template_group, name, parent_id):
        """
            Mostly used for tree view checks.
        :param session:
        :param attr_template_group:
        :param name:
        :param parent_id:
        :return:
        """


        query = session.query(Attribute_Template).filter(
            Attribute_Template.name == name,
            Attribute_Template.group_id == attr_template_group.id,
            Attribute_Template.archived == False,
            Attribute_Template.parent_id == parent_id
        )

        result = query.first()
        return result

    @staticmethod
    def get_by_name(session, attr_template_group, name):

        query = session.query(Attribute_Template).filter(
            Attribute_Template.name == name,
            Attribute_Template.group_id == attr_template_group.id,
            Attribute_Template.archived == False
        )

        result = query.first()
        return result

    @staticmethod
    def list(session,
             project_id,
             group_id,
             mode = "from_group",
             archived = False,
             limit = None,
             return_kind = "objects"
             ):
        """

        Require project id for security

        """

        if mode not in ["from_group"]:
            return

        if mode == "from_group":
            query = session.query(Attribute_Template).filter(
                Attribute_Template.project_id == project_id,
                Attribute_Template.archived == archived,
                Attribute_Template.group_id == group_id)

        # query = query.order_by(Attribute_Template.display_order)

        if return_kind == "count":
            if limit:
                query = query.limit(limit)
            return query.count()

        if return_kind == "objects":
            if limit:
                query = query.limit(limit)
            return query.all()

    def serialize(self):
        """

        """

        return {
            'id': self.id,
            'name': self.name,
            'value_type': self.value_type,
            'archived': self.archived,
            'parent_id': self.parent_id,
            'group_id': self.group_id,
            'display_order': self.display_order
        }

    @staticmethod
    def get_by_id(session,
                  id,
                  project_id = None):
        """
        Must include project id for security check

        (This assumes untrusted source)...

        """

        return session.query(Attribute_Template).filter(
            Attribute_Template.id == id,
            Attribute_Template.project_id == project_id).first()
