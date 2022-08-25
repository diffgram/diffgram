from shared.database.auth.member import Member

from sqlalchemy.orm.session import Session
from typing import List


class PermissionsChecker:

    @staticmethod
    def member_has_any_project_role(session: Session, member_id: int, roles: List[str], project_id: int) -> bool:
        from shared.database.permissions.roles import Role, RoleMemberObject, ValidObjectTypes
        if not roles:
            return False
        print('aaaas', roles)
        role_member_objects = session.query(RoleMemberObject).join(Role, Role.id == RoleMemberObject.role_id).filter(
            RoleMemberObject.object_type == ValidObjectTypes.project.name,
            Role.name.in_(roles),
            RoleMemberObject.object_id == project_id,
            RoleMemberObject.member_id == member_id
        )
        print(role_member_objects.all())
        return role_member_objects.first() is not None

    @staticmethod
    def get_allowed_object_id_list(session: Session, member: Member, object_type: str, perm: str) -> list:
        from shared.database.permissions.roles import Role, RoleMemberObject
        role_member_objects = session.query(RoleMemberObject).join(Role, Role.id == RoleMemberObject.role_id).filter(
            RoleMemberObject.object_type == object_type,
            Role.permissions_list.contains(perm),
            RoleMemberObject.member_id == member.id
        )
        obj_id_list = [elm.object_id for elm in role_member_objects]
        return obj_id_list
