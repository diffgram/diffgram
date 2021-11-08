"""Add TaskEvent Table

Revision ID: 8d8aac82ec53
Revises: bdcd484ece5f
Create Date: 2021-11-02 12:17:35.550365

"""
from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision = '8d8aac82ec53'
down_revision = '19db7c92bd14'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('task_event',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('job_id', sa.Integer(), sa.ForeignKey('member.id')),
                    sa.Column('project_id', sa.Integer(), sa.ForeignKey('project.id')),
                    sa.Column('task_id', sa.Integer(), sa.ForeignKey('task.id')),
                    sa.Column('event_type', sa.String()),
                    sa.Column('comment_id', sa.Integer(), sa.ForeignKey('discussion_comment.id')),
                    sa.Column('member_created_id', sa.Integer(), sa.ForeignKey('member.id')),
                    sa.Column('member_updated_id', sa.Integer(), sa.ForeignKey('member.id')),
                    sa.Column('time_created', sa.DateTime, default = datetime.datetime.utcnow),
                    sa.Column('time_updated', sa.DateTime, onupdate = datetime.datetime.utcnow),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('index__task_event_job_id', 'task_event', ['job_id'])
    op.create_index('index__task_event_project_id', 'task_event', ['project_id'])
    op.create_index('index__task_event_task_id', 'task_event', ['task_id'])


def downgrade():
    op.drop_index('index__task_event_task_id', 'task_event')
    op.drop_index('index__task_event_project_id', 'task_event')
    op.drop_index('index__task_event_job_id', 'task_event')
    op.drop_table('task_event')
