"""Add TaskUser Table

Revision ID: 3631b751e139
Revises: 8d8aac82ec53
Create Date: 2021-11-04 08:39:46.595503

"""
from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision = '3631b751e139'
down_revision = '8d8aac82ec53'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('task_user',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('task_id', sa.Integer(), sa.ForeignKey('task.id')),
                    sa.Column('user_id', sa.Integer(), sa.ForeignKey('userbase.id')),
                    sa.Column('relation', sa.String()),
                    sa.Column('time_created', sa.DateTime, default = datetime.datetime.utcnow),
                    sa.Column('time_updated', sa.DateTime, onupdate = datetime.datetime.utcnow),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('index__task_user_task_id', 'task_user', ['task_id'])
    op.create_index('index__task_user_user_id', 'task_user', ['user_id'])


def downgrade():
    op.drop_index('index__task_user_user_id', 'task_user')
    op.drop_index('index__task_user_task_id', 'task_user')
    op.drop_table('task_user')
