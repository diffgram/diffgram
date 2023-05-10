"""Add Text Data column to input

Revision ID: 7f4a21af81ab
Revises: 3588f18b378f
Create Date: 2023-05-09 12:34:20.053328

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f4a21af81ab'
down_revision = '3588f18b378f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('input', sa.Column('text_data', sa.String()))


def downgrade():
    op.drop_column('input', 'text_data')
    return