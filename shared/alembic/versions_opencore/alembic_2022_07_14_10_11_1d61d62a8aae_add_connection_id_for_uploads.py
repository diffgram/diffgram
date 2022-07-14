"""Add Connection ID for Uploads

Revision ID: 1d61d62a8aae
Revises: aee673edee0d
Create Date: 2022-06-27 10:11:33.781130

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1d61d62a8aae'
down_revision = 'a561aa77d88d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('file', sa.Column('connection_id', sa.Integer(), sa.ForeignKey('connection_base.id')))
    op.add_column('file', sa.Column('bucket_name', sa.String()))
    op.add_column('input', sa.Column('connection_id', sa.Integer(), sa.ForeignKey('connection_base.id')))
    op.add_column('input', sa.Column('bucket_name', sa.String()))


def downgrade():
    op.drop_column('file', 'connection_id')
    op.drop_column('file', 'bucket_name')
    op.drop_column('input', 'connection_id')
    op.drop_column('input', 'bucket_name')
