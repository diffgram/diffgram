"""add image error

Revision ID: e93e2edbb6b7
Revises: 2ef6ace7da75
Create Date: 2023-08-14 14:34:06.884101

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e93e2edbb6b7'
down_revision = '2ef6ace7da75'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('image', sa.Column('error', sa.String))


def downgrade():
    op.drop_column('image', 'error')

