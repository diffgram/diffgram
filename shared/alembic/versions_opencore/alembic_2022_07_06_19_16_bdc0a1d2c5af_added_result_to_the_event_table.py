"""Added result to the event table

Revision ID: bdc0a1d2c5af
Revises: a47884689fba
Create Date: 2022-07-06 19:16:10.894943

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bdc0a1d2c5af'
down_revision = 'a47884689fba'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('event', sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade():
    op.drop_column('event', 'result')
