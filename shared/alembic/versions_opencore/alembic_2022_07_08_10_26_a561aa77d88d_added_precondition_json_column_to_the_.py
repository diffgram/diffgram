"""Added precondition json column to the action db

Revision ID: a561aa77d88d
Revises: 2096969c6740
Create Date: 2022-07-08 10:26:43.057407

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a561aa77d88d'
down_revision = '2096969c6740'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('action', sa.Column('precondition', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade():
    op.drop_column('action', 'precondition')
