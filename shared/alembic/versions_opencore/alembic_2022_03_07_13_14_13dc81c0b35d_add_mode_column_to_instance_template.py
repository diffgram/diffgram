"""Add mode column to instance template

Revision ID: 13dc81c0b35d
Revises: 0e90db072b0b
Create Date: 2022-03-07 13:14:23.948630

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '13dc81c0b35d'
down_revision = '0e90db072b0b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('instance_template', sa.Column('mode', sa.String, default = '1_click'))


def downgrade():
    op.drop_column('instance_template', 'mode')
