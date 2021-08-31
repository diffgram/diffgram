"""Add Labelfile index for instances

Revision ID: 715370463da5
Revises: ce2ecfac6416
Create Date: 2021-08-25 10:40:18.465499

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '715370463da5'
down_revision = 'ce2ecfac6416'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('index__file_id_label_file_id', 'instance', ['file_id', 'label_file_id'])
    op.create_index('index__parent_file_id_label_file_id', 'instance', ['parent_file_id', 'label_file_id'])


def downgrade():
    op.drop_index('index__file_id_label_file_id', 'instance')
    op.drop_index('index__parent_file_id_label_file_id', 'instance')
