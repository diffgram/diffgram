"""Add Indexes Parent File ID

Revision ID: efd1cf42073a
Revises: b7921392b4c3
Create Date: 2021-12-14 14:57:28.622371

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'efd1cf42073a'
down_revision = 'b7921392b4c3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('index__parent_id_type', 'file', ['parent_id', 'type'])
    op.create_index('index__parent_id', 'file', ['parent_id'])


def downgrade():
    op.drop_index('index__parent_id_type', 'file')
    op.drop_index('index__parent_id', 'file')
