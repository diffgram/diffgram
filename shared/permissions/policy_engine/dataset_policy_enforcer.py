from shared.permissions.policy_engine.policy_engine import PermissionResult, PermissionResultObjectSet
from shared.permissions.policy_engine.base_policy_enforcer import BasePolicyEnforcer
from shared.permissions.policy_engine.policy_engine import PolicyEngine
from shared.database.permissions.roles import Role, RoleMemberObject
from shared.database.source_control.dataset_perms import DatasetDefaultRoles, DatasetRolesPermissions, DatasetPermissions
from shared.database.auth.member import Member
from sqlalchemy.orm.session import Session
from sqlalchemy import or_

from typing import List
from enum import Enum


class DatasetPolicyEnforcer(BasePolicyEnforcer):
    def __init__(self, session: Session, project: 'Project', policy_engine: PolicyEngine):
        super().__init__(session = session, project = project, policy_engine = policy_engine)
        self.session = session
        self.project = project
        self.policy_engine = policy_engine

    def list_default_roles(self, member_id: int, object_id: int) -> List[str]:
        role_names = []
        for elm in list(DatasetDefaultRoles):
            role_names.append(elm.value)

        role_member_objects = self.session.query(RoleMemberObject).filter(
            RoleMemberObject.default_role_name.in_(role_names),
            RoleMemberObject.member_id == member_id,
            RoleMemberObject.object_id == object_id
        )
        result = [elm.default_role_name for elm in role_member_objects]
        return result

    def has_perm(self, member_id: int, object_type: str, object_id: int, perm: Enum) -> PermissionResult:
        # Check Default Permissions
        default_roles = self.list_default_roles(member_id = member_id, object_id = object_id)
        for role in default_roles:
            if DatasetRolesPermissions.get(role) is not None:
                perms_list = DatasetRolesPermissions.get(role)
                if perm.value in perms_list:
                    result = PermissionResult(
                        allowed = True,
                        member_id = member_id,
                        object_type = object_type,
                        object_id = object_id
                    )
                    return result

        # Check Project Permissions
        member = Member.get_by_id(session = self.session, member_id = member_id)
        allowed_project_roles = ['viewer', 'editor', 'admin']
        if perm != DatasetPermissions.dataset_view:
            allowed_project_roles = ['editor', 'admin']
        perm_result: PermissionResult = self.policy_engine.member_has_any_project_role(member = member,
                                                                                       project_id = self.project.id,
                                                                                       roles = allowed_project_roles)
        if perm_result.allowed:
            return perm_result

        # Custom Roles checking
        perm_result = super().has_perm(member_id = member_id,
                                       object_id = object_id,
                                       object_type = object_type,
                                       perm = perm)

        return perm_result

    def get_default_roles_with_permission(self, perm: Enum) -> List[str]:
        result = []
        for role_name, perms_list in DatasetRolesPermissions.items():
            if perm.value in perms_list:
                result.append(role_name)
        return result

    def get_allowed_object_id_list(self, member: Member, object_type: Enum, perm: Enum) -> PermissionResultObjectSet:
        """
            Policy Enforcer for datasets. Here main difference is that we want to remove any datasets that
            have restricted view.
        :param member:
        :param object_type:
        :param perm:
        :return:
        """
        from shared.database.source_control.working_dir import WorkingDir
        perm_result: PermissionResult = self.policy_engine.member_has_any_project_role(member = member,
                                                                                       project_id = self.project.id,
                                                                                       roles = ['admin'])

        perm_result_set = PermissionResultObjectSet(allowed_object_id_list = [],
                                                    object_type = object_type.name,
                                                    member_id = member.id,
                                                    allow_all = perm_result.allowed)
        # Only grant all if user is admin
        if perm_result_set.allow_all:
            return perm_result_set

        perm_result: PermissionResult = self.policy_engine.member_has_any_project_role(member = member,
                                                                                       project_id = self.project.id,
                                                                                       roles = ['editor', 'viewer'])
        # If all objects are allowed, we further filter to only datasets that are not restricted
        non_restricted_ds = self.session.query(WorkingDir).filter(
            WorkingDir.project_id == self.project.id,
            or_(WorkingDir.archived == False, WorkingDir.archived.is_(None)),
            WorkingDir.access_type == 'project'
        ).all()
        print('non_restricted_ds', non_restricted_ds, self.project.id)
        non_restricted_ds_id_list = [x.id for x in non_restricted_ds]
        role_member_objects = self.session.query(RoleMemberObject) \
            .join(Role, Role.id == RoleMemberObject.role_id) \
            .join(WorkingDir, WorkingDir.id == RoleMemberObject.object_id).filter(
            RoleMemberObject.object_type == object_type.name,
            Role.permissions_list.any(perm.value),
            RoleMemberObject.member_id == member.id,
            WorkingDir.project_id == self.project.id,
            WorkingDir.access_type == 'restricted',
        ).all()
        default_roles = self.get_default_roles_with_permission(perm)
        dataset_id_from_default_roles = []
        if len(default_roles) > 0:
            default_role_member_objects = self.session.query(RoleMemberObject) \
                .join(WorkingDir, WorkingDir.id == RoleMemberObject.object_id).filter(
                RoleMemberObject.object_type == object_type.name,
                RoleMemberObject.member_id == member.id,
                RoleMemberObject.default_role_name.in_(default_roles)
            ).all()
            dataset_id_from_default_roles = [elm.object_id for elm in default_role_member_objects]
        dataset_id_list = [elm.object_id for elm in role_member_objects]
        final_dataset_id_list = dataset_id_list + non_restricted_ds_id_list + dataset_id_from_default_roles
        final_dataset_id_list = list(set(final_dataset_id_list))
        result = PermissionResultObjectSet(
            allow_all = False,
            member_id = member.id,
            object_type = object_type.name,
            allowed_object_id_list = final_dataset_id_list
        )
        return result
