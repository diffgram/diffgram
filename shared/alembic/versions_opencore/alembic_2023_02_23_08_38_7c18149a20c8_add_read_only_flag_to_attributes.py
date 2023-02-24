"""Add read only flag to attributes

Revision ID: 7c18149a20c8
Revises: 2b273b1ff1b3
Create Date: 2023-02-23 08:38:53.709659

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7c18149a20c8'
down_revision = '2b273b1ff1b3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('attribute_template_group', sa.Column('is_read_only', sa.Boolean, default = False))


def downgrade():
    op.drop_column('attribute_template_group', 'is_read_only')
