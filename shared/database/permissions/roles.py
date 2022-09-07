# OPENCORE - ADD
from shared.database.common import *
from sqlalchemy_serializer import SerializerMixin
from shared.shared_logger import get_shared_logger
from sqlalchemy.dialects import postgresql
from shared.regular.regular_log import log_has_error

from sqlalchemy.orm.attributes import flag_modified
from enum import Enum
from sqlalchemy.orm.session import Session
from typing import List
from sqlalchemy import or_, and_

logger = get_shared_logger()


class ValidObjectTypes(Enum):
    from shared.database.project import Project
    from shared.database.source_control.working_dir import WorkingDir
    project = Project
    dataset = WorkingDir


def get_valid_object_type(obj_type: str, log: dict) -> [object, dict]:
    valid_obj_types = [x.name for x in list(ValidObjectTypes)]
    print('asdasd', valid_obj_types)
    if obj_type not in valid_obj_types:
        msg = f'Invalid object type {obj_type}'
        log['error']['permission'] = msg
        logger.error(msg)
        return None, log
    return ValidObjectTypes[obj_type].value, log


class Role(Base, SerializerMixin):
    """
        Represents a role that can exist within a project.
        For now roles are objects than can just exist an be managed at the project level.
    """

    __tablename__ = 'role'

    id = Column(Integer, primary_key = True)
    name = Column(String())
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", foreign_keys = project_id)
    permissions_list = Column((postgresql.ARRAY(String)), server_default = "{}")

    @staticmethod
    def list_from_user(session: Session, member_id: int, project_id: int) -> List['Roles']:
        roles = session.query(Role).distinct(Role.id).join(RoleMemberObject,
                                                           Role.id == RoleMemberObject.role_id).filter(
            RoleMemberObject.member_id == member_id,
            Role.project_id == project_id,
        ).all()
        return roles

    @staticmethod
    def new(session, project_id, name, permissions_list = None, add_to_session = True, flush_session = True):
        role = Role(
            name = name,
            project_id = project_id,
            permissions_list = permissions_list
        )
        if add_to_session:
            session.add(role)
        if flush_session:
            session.flush()
        return role

    @staticmethod
    def list(session, project_id):
        role_list = session.query(Role).filter(
            Role.project_id == project_id
        ).all()
        return role_list

    @staticmethod
    def get_by_name_and_project(session: 'Session', project_id: int, name: str):
        role = session.query(Role).filter(
            Role.project_id == project_id,
            Role.name == name
        ).first()
        return role

    @staticmethod
    def get_by_id(session, role_id):
        role = session.query(Role).filter(
            Role.id == role_id
        ).first()
        return role

    def serialize(self):
        data = self.to_dict(rules = ('-project',))
        return data

    @staticmethod
    def check_permission_existence_for_object_type(permission: str, obj_type: str, log: dict) -> [bool, dict]:
        class_type, log = get_valid_object_type(obj_type, log)
        if log_has_error(log):
            return False, log
        perms_list = class_type.get_permissions_list()
        if permission in perms_list:
            return True, log
        else:
            msg = f'permission {permission} not in permission list {perms_list} for type{obj_type}'
            log['error']['permission'] = msg
            logger.error(msg)
            return False, log

    def add_permission(self, session, perm: str, obj_type: str, log: dict) -> ['Role', dict]:
        valid, log = Role.check_permission_existence_for_object_type(
            permission = perm,
            obj_type = obj_type,
            log = log
        )
        if not valid:
            return None, log
        if self.permissions_list is None:
            self.permissions_list = []
        self.permissions_list.append(perm)
        flag_modified(self, 'permissions_list')
        session.add(self)
        return self, log

    def remove_permission(self, session, perm: str, obj_type: str, log: dict) -> ['Role', dict]:
        valid, log = Role.check_permission_existence_for_object_type(
            permission = perm,
            obj_type = obj_type,
            log = log
        )
        if not valid:
            return None, log
        if self.permissions_list is None:
            self.permissions_list = []
        self.permissions_list.remove(perm)
        flag_modified(self, 'permissions_list')
        session.add(self)
        return self, log


class RoleMemberObject(Base, SerializerMixin):
    """
        Represents a mapping between a role and a user over an object.
        For example:
            Member ID 1 has an admin_rol on dataset ID 5
            would have
            object_id=5
            object_type=dataset
            role_id=1
            member_id=1
    """
    __tablename__ = 'role_member_object'
    id = Column(Integer, primary_key = True)
    member_id = Column(Integer, ForeignKey('member.id'))
    member = relationship('Member', foreign_keys = [member_id])

    object_id = Column(Integer)
    object_type = Column(String())

    # In case of an assignment to a default role
    default_role_name = Column(String(), nullable = True)

    role_id = Column(Integer, ForeignKey('role.id'))
    role = relationship("Role", foreign_keys = role_id)

    @staticmethod
    def check_object_type(obj_type: str, log: dict) -> [bool, dict]:
        class_type, log = get_valid_object_type(obj_type, log)
        if log_has_error(log):
            return False, log
        return True, log

    @staticmethod
    def get(session,
            member_id: int,
            object_id: int,
            object_type: Enum,
            role_id: int = None,
            default_role_name: Enum = None) -> 'RoleMemberObject':
        if role_id:
            existing = session.query(RoleMemberObject).filter(
                RoleMemberObject.member_id == member_id,
                RoleMemberObject.object_id == object_id,
                RoleMemberObject.object_type == object_type.name,
                RoleMemberObject.role_id == role_id
            ).first()
        elif default_role_name:
            existing = session.query(RoleMemberObject).filter(
                RoleMemberObject.member_id == member_id,
                RoleMemberObject.object_id == object_id,
                RoleMemberObject.object_type == object_type.name,
                RoleMemberObject.default_role_name == default_role_name
            ).first()
        return existing

    @staticmethod
    def new(session,
            member_id: int,
            object_id: int,
            object_type: Enum,
            role_id: int = None,
            default_role_name: Enum = None,
            add_to_session = True,
            flush_session = True):
        if role_id is None and default_role_name is None:
            raise Exception('Role.new() need either a default_role_name or a role_id')
        existing = None
        if role_id:
            existing = session.query(RoleMemberObject).filter(
                RoleMemberObject.member_id == member_id,
                RoleMemberObject.object_id == object_id,
                RoleMemberObject.object_type == object_type.name,
                RoleMemberObject.role_id == role_id
            ).first()
        elif default_role_name:
            existing = session.query(RoleMemberObject).filter(
                RoleMemberObject.member_id == member_id,
                RoleMemberObject.object_id == object_id,
                RoleMemberObject.object_type == object_type.name,
                RoleMemberObject.default_role_name == default_role_name
            ).first()

        if existing is not None:
            return existing
        role = RoleMemberObject(
            member_id = member_id,
            object_id = object_id,
            object_type = object_type.name,
            role_id = role_id,
        )
        if default_role_name:
            role.default_role_name = default_role_name.value
        if add_to_session:
            session.add(role)
        if flush_session:
            session.flush()
        return role

    def serialize(self):
        data = self.to_dict(rules = ('-member', '-role',))
        return data
