from shared.database.auth.member import Member

from sqlalchemy.orm.session import Session
from typing import List


class PermissionResultObjectSet:
    allowed_object_id_list: List[any]
    member: Member
    object_type: str
    allow_all: bool

    def __init__(self, allowed_object_id_list: List[any], member_id: int, object_type: str, allow_all: bool):
        self.allowed_object_id_list = allowed_object_id_list
        self.member_id = member_id
        self.object_type = object_type
        self.allow_all = allow_all


class PermissionResult:
    allowed: bool
    member_id: int
    object_type: str
    object_id: int

    def __init__(self, allowed: bool, member_id: int, object_type: str, object_id: int):
        self.allowed = allowed
        self.member_id = member_id
        self.object_id = object_id
        self.object_type = object_type


class PolicyEngine:
    session: Session

    def __init__(self, session: Session, project: 'Project'):
        self.session = session
        self.project = project

    def get_policy_enforcer(self, object_type: str) -> 'BasePolicyEnforcer':
        from shared.permissions.policy_engine.base_policy_enforcer import BasePolicyEnforcer
        POLICY_ENFORCERS_MAPPERS = {
            'dataset': None
        }
        enforcer_class = POLICY_ENFORCERS_MAPPERS.get(object_type)
        if enforcer_class is None:
            enforcer_class = BasePolicyEnforcer
        return BasePolicyEnforcer

    def member_has_perm(self,
                        member: Member,
                        object_type: str,
                        object_id: int,
                        perm: str) -> PermissionResult:
        PolicyEnforcer = self.get_policy_enforcer(object_type = object_type)
        enforcer = PolicyEnforcer(session = self.session)
        perm_result = enforcer.has_perm(member_id = member.id,
                                        object_type = object_type,
                                        object_id = object_id,
                                        perm = perm)
        return perm_result

    def member_has_any_project_role(self, member_id: int, roles: List[str],
                                    project_id: int) -> PermissionResult:
        from shared.database.permissions.roles import Role, RoleMemberObject, ValidObjectTypes
        if not roles:
            return False
        role_member_objects = self.session.query(RoleMemberObject).join(Role,
                                                                        Role.id == RoleMemberObject.role_id).filter(
            RoleMemberObject.object_type == ValidObjectTypes.project.name,
            Role.name.in_(roles),
            RoleMemberObject.object_id == project_id,
            RoleMemberObject.member_id == member_id
        )
        allowed = role_member_objects.first() is not None
        result = PermissionResult(
            allowed = allowed,
            member_id = member_id,
            object_type = ValidObjectTypes.project.name,
            object_id = project_id
        )
        return result

    def __check_member_has_default_project_role(self, member: Member, object_type: str) -> PermissionResultObjectSet:
        perm_result: PermissionResult = self.member_has_any_project_role(member_id = member.id,
                                                                         project_id = self.project.id,
                                                                         roles = ['viewer', 'editor', 'admin'])
        result = PermissionResultObjectSet(allowed_object_id_list = [],
                                           object_type = object_type,
                                           member_id = member.id,
                                           allow_all = perm_result.allowed)
        return result

    def get_allowed_object_id_list(self,
                                   member: Member,
                                   object_type: 'ValidObjectTypes',
                                   perm: str) -> PermissionResultObjectSet:
        default_roles_perm: PermissionResultObjectSet = self.__check_member_has_default_project_role(
            member = member,
            object_type = object_type
        )
        if default_roles_perm.allow_all:
            return default_roles_perm

        PolicyEnforcer = self.get_policy_enforcer(object_type = object_type)
        enforcer = PolicyEnforcer(session = self.session)
        perm_set_result = enforcer.get_allowed_object_id_list(member_id = member.id,
                                        object_type = object_type,
                                        object_id = object_id,
                                        perm = perm)

        return perm_set_result
