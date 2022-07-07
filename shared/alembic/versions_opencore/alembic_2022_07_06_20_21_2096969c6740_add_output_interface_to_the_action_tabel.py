"""Add output interface to the action tabel

Revision ID: 2096969c6740
Revises: bdc0a1d2c5af
Create Date: 2022-07-06 20:21:26.309994

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2096969c6740'
down_revision = 'bdc0a1d2c5af'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('action', sa.Column('output_interface', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade():
    op.drop_column('action', 'output_interface')
