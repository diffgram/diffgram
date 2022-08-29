from shared.permissions.policy_engine.policy_engine import PermissionResult, PermissionResultObjectSet
from shared.database.permissions.roles import Role, RoleMemberObject
from sqlalchemy.orm.session import Session


class BasePolicyEnforcer:
    def __init__(self, session: Session):
        self.session = session

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

    def get_allowed_object_id_list(self, member_id: int, object_type: str, object_id: int,
                                   perm: str) -> PermissionResultObjectSet:
        # Check for default permissions first.

        role_member_objects = self.session.query(RoleMemberObject).join(Role,
                                                                        Role.id == RoleMemberObject.role_id).filter(
            RoleMemberObject.object_type == object_type.name,
            Role.permissions_list.any(perm),
            RoleMemberObject.member_id == member_id
        )
        obj_id_list = [elm.object_id for elm in role_member_objects]
        result = PermissionResultObjectSet(
            allow_all = False,
            member_id = member_id,
            object_type = object_type,
            allowed_object_id_list = obj_id_list
        )
        return result
