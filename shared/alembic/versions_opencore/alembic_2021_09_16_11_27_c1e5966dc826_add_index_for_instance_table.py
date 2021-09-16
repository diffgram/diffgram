"""Add Index for Instance Table

Revision ID: c1e5966dc826
Revises: 715370463da5
Create Date: 2021-09-16 11:27:53.283096

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1e5966dc826'
down_revision = '715370463da5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('index__task_id', 'instance', ['task_id'])
    op.create_index('index__created_time', 'instance', ['created_time'])
    op.create_index('index__task_id_label_file_id', 'instance', ['task_id', 'label_file_id'])


def downgrade():
    op.drop_index('index__task_id', 'instance')
    op.drop_index('index__created_time', 'created_time')
    op.drop_index('index__task_id_label_file_id', 'instance')
