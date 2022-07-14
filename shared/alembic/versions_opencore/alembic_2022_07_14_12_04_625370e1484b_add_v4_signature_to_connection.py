"""Add v4 signature to connection

Revision ID: 625370e1484b
Revises: 1d61d62a8aae
Create Date: 2022-07-14 12:04:49.577650

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '625370e1484b'
down_revision = '1d61d62a8aae'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('connection_base', sa.Column('aws_v4_signature', sa.Boolean()))


def downgrade():
    op.drop_column('connection_base', 'aws_v4_signature')
