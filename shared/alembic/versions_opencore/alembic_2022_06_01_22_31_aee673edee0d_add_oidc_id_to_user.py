"""Add OIDC id to user

Revision ID: aee673edee0d
Revises: 3feda3d442be
Create Date: 2022-06-01 22:31:34.222461

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aee673edee0d'
down_revision = '501d8176d48f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('userbase', sa.Column('oidc_id', sa.String()))


def downgrade():
    op.drop_column('userbase', 'oidc_id')
