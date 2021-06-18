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


def downgrade():
    op.drop_column('file', 'file_metadata')
