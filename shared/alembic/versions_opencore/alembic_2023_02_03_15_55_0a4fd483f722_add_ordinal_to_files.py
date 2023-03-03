"""Add ordinal to files

Revision ID: 0a4fd483f722
Revises: 118611274c7f
Create Date: 2023-02-03 15:55:19.814401

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0a4fd483f722'
down_revision = '118611274c7f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('file',  sa.Column('ordinal', sa.Integer(), default = 0))
    op.add_column('input',  sa.Column('ordinal', sa.Integer(), default = 0))


def downgrade():
    op.drop_column('file', 'ordinal')
    op.drop_column('input', 'ordinal')
