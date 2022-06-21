"""improve ai

Revision ID: a47884689fba
Revises: aee673edee0d
Create Date: 2022-06-07 16:51:02.670055

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = 'a47884689fba'
down_revision = 'aee673edee0d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('instance', sa.Column('score', sa.Float))
    op.add_column('action', sa.Column('output', JSONB))
    op.add_column('action_run', sa.Column('output', JSONB))


def downgrade():
    op.drop_column('instance', 'score')
    op.drop_column('action', 'output')
    op.drop_column('action_run', 'output')
