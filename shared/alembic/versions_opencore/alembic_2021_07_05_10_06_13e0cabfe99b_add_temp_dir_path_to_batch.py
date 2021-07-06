"""Add Temp Dir path to batch

Revision ID: 13e0cabfe99b
Revises: d4c89390cad8
Create Date: 2021-07-05 10:06:59.445412

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '13e0cabfe99b'
down_revision = 'd4c89390cad8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('input_batch', sa.Column('data_temp_dir', sa.String))


def downgrade():
    op.drop_column('input_batch', 'data_temp_dir')
