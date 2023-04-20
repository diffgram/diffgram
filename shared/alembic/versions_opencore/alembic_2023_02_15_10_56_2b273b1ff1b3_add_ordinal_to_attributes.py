"""Add ordinal to Attributes

Revision ID: 2b273b1ff1b3
Revises: 0a4fd483f722
Create Date: 2023-02-15 10:56:21.853117

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2b273b1ff1b3'
down_revision = '0a4fd483f722'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('attribute_template_group', sa.Column('ordinal', sa.Integer(), default = 0))


def downgrade():
    op.drop_column('attribute_template_group', 'ordinal')
