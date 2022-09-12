from shared.database.auth.member import Member
from enum import Enum
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
    object_id_list: List[int]

    def __init__(self, allowed: bool, member_id: int, object_type: str, object_id: int = None, object_id_list: List[int] = None):
        self.allowed = allowed
        self.member_id = member_id
        self.object_id = object_id
        self.object_type = object_type
        self.object_id_list = object_id_list


class PolicyEngine:
    session: Session

    def __init__(self, session: Session, project: 'Project'):
        self.session = session
        self.project = project

    def get_policy_enforcer(self, object_type: Enum) -> 'BasePolicyEnforcer':
        from shared.permissions.policy_engine.base_policy_enforcer import BasePolicyEnforcer
        from shared.permissions.policy_engine.dataset_policy_enforcer import DatasetPolicyEnforcer
        from shared.permissions.policy_engine.file_policy_enforcer import FilePolicyEnforcer
        POLICY_ENFORCERS_MAPPERS = {
            'WorkingDir': DatasetPolicyEnforcer,
            'File': FilePolicyEnforcer
        }
        enforcer_class = POLICY_ENFORCERS_MAPPERS.get(object_type.name)
        if enforcer_class is None:
            enforcer_class = BasePolicyEnforcer
        return enforcer_class

    def member_has_perm(self,
                        member: Member,
                        object_type: Enum,
                        object_id: int,
                        perm: Enum) -> PermissionResult:
        if member.user and member.user.is_super_admin:
            result = PermissionResult(
                allowed = True,
                member_id = member.id,
                object_type = object_type.name,
                object_id = object_id
            )
            return result
        PolicyEnforcer = self.get_policy_enforcer(object_type = object_type)
        enforcer = PolicyEnforcer(session = self.session, project = self.project, policy_engine = self)
        perm_result = enforcer.has_perm(member_id = member.id,
                                        object_type = object_type.name,
                                        object_id = object_id,
                                        perm = perm)
        return perm_result

    def member_has_any_project_role(self,
                                    member: Member,
                                    roles: list,
                                    project_id: int) -> PermissionResult:
        from shared.database.permissions.roles import Role, RoleMemberObject, ValidObjectTypes
        if not roles:
            return False
        role_member_objects = self.session.query(RoleMemberObject).join(Role,
                                                                        Role.id == RoleMemberObject.role_id).filter(
            RoleMemberObject.object_type == ValidObjectTypes.project.name,
            Role.name.in_(roles),
            RoleMemberObject.object_id == project_id,
            RoleMemberObject.member_id == member.id
        )

        allowed = role_member_objects.first() is not None
        if member.user and member.user.is_super_admin:
            allowed = True

        default_role_member_objects = self.session.query(RoleMemberObject).filter(
            RoleMemberObject.object_type == ValidObjectTypes.project.name,
            RoleMemberObject.default_role_name.in_(roles),
            RoleMemberObject.object_id == project_id,
            RoleMemberObject.member_id == member.id
        )
        if not allowed:
            allowed = default_role_member_objects.first() is not None
        result = PermissionResult(
            allowed = allowed,
            member_id = member.id,
            object_type = ValidObjectTypes.project.name,
            object_id = project_id
        )
        return result

    def get_allowed_object_id_list(self,
                                   member: Member,
                                   object_type: Enum,
                                   perm: Enum) -> PermissionResultObjectSet:

        PolicyEnforcer = self.get_policy_enforcer(object_type = object_type)
        enforcer = PolicyEnforcer(session = self.session, project = self.project, policy_engine = self)
        perm_set_result = enforcer.get_allowed_object_id_list(member = member,
                                                              object_type = object_type,
                                                              perm = perm)

        return perm_set_result
