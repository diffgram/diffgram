"""Roles 2.0

Revision ID: c6094792feeb
Revises: 625370e1484b
Create Date: 2022-07-25 10:32:54.987025

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm.session import Session

from shared.database.user import User
from shared.database.auth.api import Auth_api
from shared.database.permissions.roles import RoleMemberObject, Role, ValidObjectTypes
from shared.database.project_perms import ProjectRolesPermissions, ProjectDefaultRoles
# revision identifiers, used by Alembic.
revision = 'c6094792feeb'
down_revision = 'f098a0aa6959'
branch_labels = None
depends_on = None


def migrate_roles_from_project(op):
    """
        Not used. As a backup plan in case a migration is needed.
        For now, all default roles will be managed in the codebase.
    :param op:
    :return:
    """
    bind = op.get_bind()
    session = Session(bind = bind)
    from shared.database.project import Project
    all_projects = session.query(Project).all()
    for project in all_projects:
        # First Create default Roles for project.
        project.create_default_roles(session = session)
        print(f'Created default roles for {project.project_string_id}')
    all_users = session.query(User).all()
    for user in all_users:
        permissions_dict = user.permissions_projects
        if permissions_dict is None:
            continue
        for project_string_id, roles_list in permissions_dict.items():
            project = Project.get_by_string_id(session = session, project_string_id = project_string_id)
            for role_name in roles_list:
                if role_name.lower() in ProjectRolesPermissions.keys():
                    RoleMemberObject.new(
                        session = session,
                        default_role_name = ProjectDefaultRoles[role_name.lower()],
                        member_id = user.member_id,
                        object_id = project.id,
                        object_type = ValidObjectTypes.project
                    )
                print(f'Added {role_name} to user {user.member_id} on project {project_string_id}')
    # Now migrate API Accesses
    api_members = session.query(Auth_api).all()
    for api in api_members:
        role_name = api.permission_level
        if role_name is None:
            continue
        project = Project.get_by_string_id(session = session, project_string_id = api.project_string_id)
        if project is None:
            continue
        if role_name.lower() in ProjectRolesPermissions.keys():
            RoleMemberObject.new(
                session = session,
                default_role_name = ProjectDefaultRoles[role_name.lower()],
                member_id = api.member_id,
                object_id = project.id,
                object_type = ValidObjectTypes.project
            )
            print(f'Added {role_name.lower()} to API Access {api.member_id} on project {api.project_string_id}')
def upgrade():
    op.create_table('role',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('project_id', sa.Integer(), sa.ForeignKey('project.id')),
                    sa.Column('name', sa.String()),
                    sa.Column('permissions_list', ARRAY(sa.String)),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('index__role_project', 'role', ['project_id'])

    op.create_table('role_member_object',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('member_id', sa.Integer(), sa.ForeignKey('member.id')),
                    sa.Column('object_id', sa.Integer()),
                    sa.Column('object_type', sa.String()),
                    sa.Column('default_role_name', sa.String(), nullable = True),
                    sa.Column('role_id', sa.Integer(), sa.ForeignKey('role.id')),
                    sa.PrimaryKeyConstraint('id'))
    op.create_index('index__role_user_object_member_id', 'role_member_object', ['member_id'])
    op.create_index('index__role_user_object_default_role_name', 'role_member_object', ['default_role_name'])
    op.create_index('index__role_user_object_object_id', 'role_member_object', ['object_id'])
    op.create_index('index__role_user_object_role_id', 'role_member_object', ['role_id'])
    op.create_index('index__role_user_object_role_id_member_id', 'role_member_object', ['role_id', 'member_id'])
    op.create_index('index__role_user_object_default_role_name_member_id', 'role_member_object',
                    ['default_role_name', 'member_id'])
    op.create_index('index__role_user_object_role_id_object_id', 'role_member_object', ['role_id', 'object_id'])
    op.create_index('index__role_user_object_default_role_name_object_id', 'role_member_object',
                    ['default_role_name', 'object_id'])

    op.add_column('working_dir', sa.Column('access_type', sa.String(), default = 'project', nullable=False, server_default='project'))
    op.create_index('index__working_dir_access_type_project', 'working_dir', ['project_id', 'access_type'])
    op.create_index('index__working_dir_access_type', 'working_dir', ['access_type'])

    migrate_roles_from_project(op)


def downgrade():
    op.drop_index('index__role_user_object_member_id', 'role_member_object')
    op.drop_index('index__role_user_object_object_id', 'role_member_object')
    op.drop_index('index__role_user_object_role_id', 'role_member_object')
    op.drop_index('index__role_user_object_role_id_member_id', 'role_member_object')
    op.drop_index('index__role_user_object_role_id_object_id', 'role_member_object')
    op.drop_index('index__working_dir_access_type', 'working_dir')
    op.drop_index('index__working_dir_access_type_project', 'working_dir')
    op.drop_table('role_member_object')
    op.drop_column('working_dir', 'access_type')

    op.drop_index('index__role_project', 'role')
    op.drop_table('role')
