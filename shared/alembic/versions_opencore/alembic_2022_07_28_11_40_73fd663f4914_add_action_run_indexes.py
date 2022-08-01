"""Add Action Run Indexes

Revision ID: 73fd663f4914
Revises: ee0b773d7266
Create Date: 2022-07-28 11:40:30.041858

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '73fd663f4914'
down_revision = 'ee0b773d7266'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('index__action_run_action_id', 'action_run', ['action_id'])
    op.create_index('index__action_run_project_id_action_id', 'action_run', ['project_id', 'action_id'])
    op.create_index('index__action_run_project_id', 'action_run', ['project_id'])
    op.add_column('action_run', sa.Column('status', sa.String()))


def downgrade():
    op.drop_index('index__action_run_project_id', 'action_run')
    op.drop_index('index__action_run_project_id_action_id', 'action_run')
    op.drop_index('index__action_run_action_id', 'action_run')
    op.drop_column('action_run', 'status')
