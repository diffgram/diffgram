from shared.permissions.policy_engine.policy_engine import PermissionResult, PermissionResultObjectSet
from shared.permissions.policy_engine.base_policy_enforcer import BasePolicyEnforcer
from shared.permissions.policy_engine.policy_engine import PolicyEngine
from shared.database.permissions.roles import Role, RoleMemberObject, ValidObjectTypes
from shared.database.source_control.file_perms import FileDefaultRoles, FileRolesPermissions, FilePermissions
from shared.database.source_control.dataset_perms import DatasetPermissions, DatasetDefaultRoles
from shared.database.auth.member import Member
from shared.database.source_control.file import File
from shared.permissions.policy_engine.dataset_policy_enforcer import DatasetPolicyEnforcer
from shared.database.project_perms import ProjectDefaultRoles
from sqlalchemy.orm.session import Session
from sqlalchemy import or_

from typing import List
from enum import Enum


class FilePolicyEnforcer(BasePolicyEnforcer):
    def __init__(self, session: Session, project: 'Project', policy_engine: PolicyEngine):
        super().__init__(session = session, project = project, policy_engine = policy_engine)
        self.session = session
        self.project = project
        self.policy_engine = policy_engine

    def list_default_roles(self, member_id: int, object_id: int) -> List[str]:
        role_names = []
        for elm in list(FileDefaultRoles):
            role_names.append(elm.value)

        role_member_objects = self.session.query(RoleMemberObject).filter(
            RoleMemberObject.default_role_name.in_(role_names),
            RoleMemberObject.member_id == member_id,
            RoleMemberObject.object_id == object_id
        )
        result = [elm.default_role_name for elm in role_member_objects]
        return result

    def __has_perm_from_dataset(self, member_id: int, object_id: int, perm: Enum) -> PermissionResult:
        dataset_id_list = File.get_directories_ids(session = self.session, file_id = object_id)
        ds_policy_enforcer = DatasetPolicyEnforcer(session = self.session, project = self.project,
                                                   policy_engine = self.policy_engine)
        ds_perm = DatasetPermissions.dataset_edit
        if perm == FilePermissions.file_view:
            ds_perm = DatasetPermissions.dataset_view
        elif perm == FilePermissions.file_edit:
            ds_perm = DatasetPermissions.dataset_edit
        elif perm == FilePermissions.file_delete:
            ds_perm = DatasetPermissions.dataset_delete

        perm_result: PermissionResult = ds_policy_enforcer.has_perm_for_at_least_one(
            member_id = member_id,
            object_type = ValidObjectTypes.dataset.name,
            object_id_list = dataset_id_list,
            perm = ds_perm,
        )
        return perm_result

    def has_perm(self, member_id: int, object_type: str, object_id: int, perm: Enum) -> PermissionResult:
        # Check Default Permissions
        default_roles = self.list_default_roles(member_id = member_id, object_id = object_id)
        for role in default_roles:
            if FileRolesPermissions.get(role) is not None:
                perms_list = FileRolesPermissions.get(role)
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
        allowed_project_roles = [ProjectDefaultRoles.viewer.value,
                                 ProjectDefaultRoles.editor.value,
                                 ProjectDefaultRoles.admin.value]
        if perm != FilePermissions.file_view:
            allowed_project_roles = [ProjectDefaultRoles.editor.value,
                                     ProjectDefaultRoles.admin.value]
        perm_result: PermissionResult = self.policy_engine.member_has_any_project_role(member = member,
                                                                                       project_id = self.project.id,
                                                                                       roles = allowed_project_roles)
        if perm_result.allowed:
            return perm_result

        # Check Dataset Permissions
        perm_result: PermissionResult = self.__has_perm_from_dataset(
            member_id = member_id,
            object_id = object_id,
            perm = perm
        )
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
        for role_name, perms_list in FileRolesPermissions.items():
            if perm.value in perms_list:
                result.append(role_name)
        return result
