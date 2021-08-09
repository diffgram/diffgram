"""Add Labelfile index for instances

Revision ID: f75d238e6529
Revises: 3e67f31e1a08
Create Date: 2021-08-09 15:33:51.933934

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f75d238e6529'
down_revision = '3e67f31e1a08'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('index__file_id_label_file_id', 'instance', ['file_id', 'label_file_id'])
    op.create_index('index__parent_file_id_label_file_id', 'instance', ['parent_file_id', 'label_file_id'])


def downgrade():
    op.drop_index('index__file_id_label_file_id', 'instance')
    op.drop_index('index__parent_file_id_label_file_id', 'instance')
