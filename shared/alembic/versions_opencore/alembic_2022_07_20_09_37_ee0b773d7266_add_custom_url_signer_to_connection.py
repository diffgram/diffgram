"""Add custom url signer to connection

Revision ID: ee0b773d7266
Revises: 625370e1484b
Create Date: 2022-07-20 09:37:28.627776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee0b773d7266'
down_revision = 'bfb007d3c340'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('connection_base', sa.Column('url_signer_service', sa.String(), default=None))


def downgrade():
    op.drop_column('connection_base', 'url_signer_service')