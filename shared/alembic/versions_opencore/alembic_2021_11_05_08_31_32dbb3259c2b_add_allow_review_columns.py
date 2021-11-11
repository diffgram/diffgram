"""Add Allow Review Columns

Revision ID: 32dbb3259c2b
Revises: 3631b751e139
Create Date: 2021-11-05 08:31:12.207925

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32dbb3259c2b'
down_revision = '3631b751e139'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('job', sa.Column('allow_reviews', sa.Boolean(), default = False))


def downgrade():
    op.drop_column('job', 'allow_reviews')
