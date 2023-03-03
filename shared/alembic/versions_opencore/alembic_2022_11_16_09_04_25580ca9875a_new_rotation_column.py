"""New Rotation Column

Revision ID: 25580ca9875a
Revises: 61977555605b
Create Date: 2022-11-15 09:04:17.395177

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '25580ca9875a'
down_revision = 'f1b006dd9e9e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('image', sa.Column('rotation_degrees', sa.Integer(), default = 0))


def downgrade():
    op.drop_column('image', 'rotation_degrees')
