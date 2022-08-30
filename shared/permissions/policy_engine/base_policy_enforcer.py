from shared.permissions.policy_engine.policy_engine import PermissionResult, PermissionResultObjectSet, PolicyEngine
from shared.database.permissions.roles import Role, RoleMemberObject
from enum import Enum
from sqlalchemy.orm.session import Session
from shared.database.auth.member import Member

class BasePolicyEnforcer:
    session: Session
    project: 'Project'
    policy_engine: PolicyEngine

    def __init__(self, session: Session, project: 'Project', policy_engine: PolicyEngine):
        self.session = session
        self.project = project
        self.policy_engine = policy_engine

    def __check_member_has_default_project_role(self, member: Member, object_type: str) -> PermissionResultObjectSet:
        perm_result: PermissionResult = self.policy_engine.member_has_any_project_role(member = member,
                                                                                       project_id = self.project.id,
                                                                                       roles = ['viewer', 'editor',
                                                                                                'admin'])
        result = PermissionResultObjectSet(allowed_object_id_list = [],
                                           object_type = object_type,
                                           member_id = member.id,
                                           allow_all = perm_result.allowed)
        return result

    def has_perm(self, member_id: int, object_type: str, object_id: int, perm: str) -> PermissionResult:
        role_member_objects = self.session.query(RoleMemberObject).join(Role,
                                                                        Role.id == RoleMemberObject.role_id).filter(
            RoleMemberObject.object_type == object_type,
            Role.permissions_list.any(perm),
            RoleMemberObject.member_id == member_id,
            RoleMemberObject.object_id == object_id
        )
        allowed = role_member_objects.first() is not None
        result = PermissionResult(
            allowed = allowed,
            member_id = member_id,
            object_type = object_type,
            object_id = object_id
        )
        return result

    def get_allowed_object_id_list(self,
                                   member: Member,
                                   object_type: Enum,
                                   perm: Enum) -> PermissionResultObjectSet:
        # Check for default permissions first.
        default_roles_perm: PermissionResultObjectSet = self.__check_member_has_default_project_role(
            member = member,
            object_type = object_type.name
        )
        if default_roles_perm.allow_all:
            return default_roles_perm

        role_member_objects = self.session.query(RoleMemberObject).join(Role,
                                                                        Role.id == RoleMemberObject.role_id).filter(
            RoleMemberObject.object_type == object_type.name,
            Role.permissions_list.any(perm.name),
            RoleMemberObject.member_id == member.id
        )
        obj_id_list = [elm.object_id for elm in role_member_objects]
        result = PermissionResultObjectSet(
            allow_all = False,
            member_id = member.id,
            object_type = object_type.name,
            allowed_object_id_list = obj_id_list
        )
        return result
