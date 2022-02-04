"""Add Time Tracking Table

Revision ID: a9023fc32298
Revises: ddcdf79c4cbc
Create Date: 2022-02-04 10:56:29.217844

"""
from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision = 'a9023fc32298'
down_revision = 'ddcdf79c4cbc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('task_time_tracking',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('task_id', sa.Integer(), sa.ForeignKey('task.id')),
                    sa.Column('job_id', sa.Integer(), sa.ForeignKey('job.id')),
                    sa.Column('project_id', sa.Integer(), sa.ForeignKey('project.id')),
                    sa.Column('status', sa.String(), nullable = True),
                    sa.Column('user_id', sa.Integer(), sa.ForeignKey('userbase.id')),
                    sa.Column('file_id', sa.Integer(), sa.ForeignKey('file.id')),
                    sa.Column('parent_file_id', sa.Integer(), sa.ForeignKey('file.id'), nullable = True),
                    sa.Column('time_spent', sa.Float(), nullable = False),
                    sa.Column('time_created', sa.DateTime, default = datetime.datetime.utcnow),
                    sa.Column('time_updated', sa.DateTime, onupdate = datetime.datetime.utcnow),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('index__task_time_tracking_task_id', 'task_time_tracking', ['task_id'])
    op.create_index('index__task_time_tracking_job_id', 'task_time_tracking', ['job_id'])
    op.create_index('index__task_time_tracking_project_id', 'task_time_tracking', ['project_id'])
    op.create_index('index__task_time_tracking_user_id', 'task_time_tracking', ['user_id'])
    op.create_index('index__task_time_tracking_task_id_status', 'task_time_tracking', ['task_id', 'status'])
    op.create_index('index__task_time_tracking_job_id_status', 'task_time_tracking', ['job_id', 'status'])
    op.create_index('index__task_time_tracking_parent_file', 'task_time_tracking', ['parent_file_id', 'task_id'])

    op.create_unique_constraint('unique_time_record',
                                'task_time_tracking',
                                ['task_id', 'project_id', 'job_id', 'status', 'user_id', 'file_id', 'parent_file_id'])


def downgrade():
    op.drop_index('index__task_time_tracking_task_id', 'task_time_tracking')
    op.drop_index('index__task_time_tracking_job_id', 'task_time_tracking')
    op.drop_index('index__task_time_tracking_project_id', 'task_time_tracking')
    op.drop_index('index__task_time_tracking_user_id', 'task_time_tracking')
    op.drop_index('index__task_time_tracking_task_id_status', 'task_time_tracking')
    op.drop_index('index__task_time_tracking_job_id_status', 'task_time_tracking')
    op.drop_index('index__task_time_tracking_parent_file', 'task_time_tracking')
    op.drop_constraint('unique_time_record', 'task_time_tracking')
    op.drop_table('task_time_tracking')
