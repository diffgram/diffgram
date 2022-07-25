"""Roles 2.0

Revision ID: c6094792feeb
Revises: 625370e1484b
Create Date: 2022-07-25 10:32:54.987025

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import ARRAY

# revision identifiers, used by Alembic.
revision = 'c6094792feeb'
down_revision = '625370e1484b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('role',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('project_id', sa.Integer(), sa.ForeignKey('project.id')),
                    sa.Column('permissions_list', sa.Integer(), sa.ForeignKey('userbase.id')),
                    sa.Column('name', ARRAY(sa.String)),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('index__role_project', 'role', ['project_id'])

    op.create_table('role_member_object',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('member_id', sa.Integer(), sa.ForeignKey('member.id')),
                    sa.Column('object_id', sa.Integer()),
                    sa.Column('role_id', sa.Integer(), sa.ForeignKey('role.id')),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('index__role_user_object_member_id', 'role_member_object', ['member_id'])
    op.create_index('index__role_user_object_object_id', 'role_member_object', ['object_id'])
    op.create_index('index__role_user_object_role_id', 'role_member_object', ['role_id'])
    op.create_index('index__role_user_object_role_id_member_id', 'role_member_object', ['role_id', 'member_id'])
    op.create_index('index__role_user_object_role_id_object_id', 'role_member_object', ['role_id', 'object_id'])


def downgrade():
    op.drop_index('index__role_user_object_member_id', 'role_member_object')
    op.drop_index('index__role_user_object_object_id', 'role_member_object')
    op.drop_index('index__role_user_object_role_id', 'role_member_object')
    op.drop_index('index__role_user_object_role_id_member_id', 'role_member_object')
    op.drop_index('index__role_user_object_role_id_object_id', 'role_member_object')
    op.drop_table('role_member_object')

    op.drop_index('index__role_project', 'role')
    op.drop_table('role')
