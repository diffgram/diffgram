# OPENCORE - ADD
from shared.database.common import *
from sqlalchemy_serializer import SerializerMixin


class Role(Base, SerializerMixin):
    """
        Represents a role that can exist within a project.
        For now roles are objects than can just exist an be managed at the project level.
    """

    __tablename__ = 'role'

    id = Column(Integer, primary_key = True)
    name = Column(String(250))
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", back_populates = "star_list",
                           foreign_keys = project_id)
    occupation_list = Column((ARRAY(String)))


class RolePermission(Base, SerializerMixin):
    """
        Represents a mapping between a role an a permission over an object.
        For example:
            an admin_rol can delete dataset ID 5
            would have
            object_id=5
            object_type=dataset
            role_id=1
            permission="delete"
    """
    __tablename__ = 'role_permission'
    member_id = Column(Integer, ForeignKey('member.id'))
    member = relationship('Member', foreign_keys = [member_id])


    object_id = Column(Integer)
    object_type = Column(String())

    role_id = Column(Integer, ForeignKey('role.id'))
    role = relationship("Role", foreign_keys = role_id)

    permission = Column(String())


class RoleMember(Base, SerializerMixin):
    """
        Mapping between a role and a member of Diffgram.
    """
    __tablename__ = 'role_member'
    role_id = Column(Integer, ForeignKey('role.id'))
    role = relationship("Role", foreign_keys = role_id)

