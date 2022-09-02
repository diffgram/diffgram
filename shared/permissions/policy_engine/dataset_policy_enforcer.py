from shared.permissions.policy_engine.policy_engine import PermissionResult, PermissionResultObjectSet
from shared.permissions.policy_engine.base_policy_enforcer import BasePolicyEnforcer
from shared.permissions.policy_engine.policy_engine import PolicyEngine
from shared.database.permissions.roles import Role, RoleMemberObject
from shared.database.source_control.dataset_perms import DatasetDefaultRoles, DatasetRolesPermissions
from shared.database.auth.member import Member
from sqlalchemy.orm.session import Session
from typing import List


class DatasetPolicyEnforcer(BasePolicyEnforcer):
    def __init__(self, session: Session, project: 'Project', policy_engine: PolicyEngine):
        self.session = session
        self.project = project
        self.policy_engine = policy_engine

    def has_perm(self, member_id: int, object_type: str, object_id: int, perm: str) -> PermissionResult:
        # Check Default Permissions

        roles = Role.list_from_user(session = self.session, member_id = member_id, project_id = self.project.id)
        for role in roles:
            if DatasetRolesPermissions.get(role.name) is not None:
                perms_list = DatasetRolesPermissions.get(role.name)
                if perm in perms_list:
                    result = PermissionResult(
                        allowed = True,
                        member_id = member_id,
                        object_type = object_type,
                        object_id = object_id
                    )
                    return result

        perm_result = super(self).has_perm(member_id = member_id,
                                           object_id = object_id,
                                           perm = perm)

        return perm_result

    def get_default_roles_with_permission(self, perm: str) -> List[str]:
        result = []
        for role_name, perms_list in DatasetRolesPermissions:
            if perm in perms_list:
                result.append(role_name)
        return result

    def get_allowed_object_id_list(self, member: Member, object_type: str, perm: str) -> PermissionResultObjectSet:
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
                                                    object_type = object_type,
                                                    member_id = member.id,
                                                    allow_all = perm_result.allowed)
        # Only grant all if user is admin
        if perm_result_set.allow_all:
            return perm_result_set

        # If all objects are allowed, we further filter to only datasets that are not restricted
        non_restricted_ds = self.session.query(WorkingDir).filter(
            WorkingDir.project_id == self.project.id,
            WorkingDir.archived == False,
            WorkingDir.access_type == 'project'
        )

        role_member_objects = self.session.query(RoleMemberObject) \
            .join(Role, Role.id == RoleMemberObject.role_id) \
            .join(WorkingDir, WorkingDir.id == RoleMemberObject.object_id).filter(
            RoleMemberObject.object_type == object_type.name,
            Role.permissions_list.any(perm),
            RoleMemberObject.member_id == member.id,
            WorkingDir.project_id == self.project.id,
            WorkingDir.access_type == 'restricted',


        )
        default_roles = self.get_default_roles_with_permission(perm)
        dataset_id_from_default_roles = []
        if len(default_roles) > 0:
            default_role_member_objects = self.session.query(RoleMemberObject) \
                .join(WorkingDir, WorkingDir.id == RoleMemberObject.object_id).filter(
                RoleMemberObject.object_type == object_type.name,
                RoleMemberObject.member_id == member.id,
                WorkingDir.member_id == member.id
            )
            dataset_id_from_default_roles = [elm.object_id for elm in default_role_member_objects]
        dataset_id_list = [elm.object_id for elm in role_member_objects]
        final_dataset_id_list = dataset_id_list + non_restricted_ds + dataset_id_from_default_roles
        final_dataset_id_list = list(set(final_dataset_id_list))
        result = PermissionResultObjectSet(
            allow_all = False,
            member_id = member.id,
            object_type = object_type,
            allowed_object_id_list = final_dataset_id_list
        )
        return result
