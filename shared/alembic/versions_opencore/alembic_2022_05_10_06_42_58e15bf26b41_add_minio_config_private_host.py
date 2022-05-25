"""add minio config private_host

Revision ID: 58e15bf26b41
Revises: e7d84ad133ea
Create Date: 2022-05-10 06:42:33.563029

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '58e15bf26b41'
down_revision = 'e7d84ad133ea'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('connection_base', sa.Column('private_host', sa.String(), nullable=True))
    op.add_column('connection_base', sa.Column('disabled_ssl_verify', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('connection_base', 'private_host')
    op.drop_column('connection_base', 'disabled_ssl_verify')

