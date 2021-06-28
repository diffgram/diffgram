"""Add File Metadata

Revision ID: d4c89390cad8
Revises: 94ac4e48a114
Create Date: 2021-06-18 14:18:21.645050

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = 'd4c89390cad8'
down_revision = '94ac4e48a114'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('file', sa.Column('file_metadata', JSONB))
    op.add_column('input', sa.Column('file_metadata', JSONB))
    op.create_index('index__file_id__and__label_id', 'instance', ['file_id', 'label_file_id'])
    op.create_index('index__parent_id__and__label_id', 'instance', ['parent_file_id', 'label_file_id'])


def downgrade():
    op.drop_column('file', 'file_metadata')
    op.drop_column('input', 'file_metadata')
    op.drop_index('index__file_id__and__label_id', 'instance')
    op.drop_index('index__parent_id__and__label_id', 'instance')
