"""Add Reviewer and assignee to Task Events

Revision ID: 0e90db072b0b
Revises: 4b2b0450b93b
Create Date: 2022-02-22 10:32:25.966134

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0e90db072b0b'
down_revision = '4b2b0450b93b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('task_event', sa.Column('user_assignee_id', sa.Integer, sa.ForeignKey('userbase.id')))
    op.add_column('task_event', sa.Column('user_reviewer_id', sa.Integer, sa.ForeignKey('userbase.id')))

    op.create_index('index__job_id', 'task_event', ['job_id'])
    op.create_index('index__task_id', 'task_event', ['task_id'])
    op.create_index('index__job_id_user_assignee_id', 'task_event', ['job_id', 'user_assignee_id'])
    op.create_index('index__job_id_user_reviewer_id', 'task_event', ['job_id', 'user_reviewer_id'])
    op.create_index('index_user_reviewer_id', 'task_event', ['user_reviewer_id'])
    op.create_index('index_user_assignee_id', 'task_event', ['user_assignee_id'])
    op.create_index('index_member_created_id', 'task_event', ['member_created_id'])


def downgrade():
    op.drop_column('task_event', 'user_assignee_id')
    op.drop_column('task_event', 'user_reviewer_id')
    op.drop_index('index__job_id', 'task_event')
    op.drop_index('index__task_id', 'task_event')
    op.drop_index('index__job_id_user_assignee_id', 'task_event')
    op.drop_index('index__job_id_user_reviewer_id', 'task_event')
    op.drop_index('index_user_reviewer_id', 'task_event')
    op.drop_index('index_user_assignee_id', 'task_event')
    op.drop_index('index_member_created_id', 'task_event')
