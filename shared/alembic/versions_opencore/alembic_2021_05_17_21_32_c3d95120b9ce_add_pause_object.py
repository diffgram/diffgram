"""add pause_object

Revision ID: c3d95120b9ce
Revises: 77907aedd319
Create Date: 2021-05-17 21:32:46.140955

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d95120b9ce'
down_revision = '77907aedd319'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('instance', sa.Column('pause_object', sa.Boolean()))


def downgrade():
    op.drop_column('instance', 'pause_object')
