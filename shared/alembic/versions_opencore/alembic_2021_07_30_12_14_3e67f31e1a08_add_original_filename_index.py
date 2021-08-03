"""Add Original Filename Index

Revision ID: 3e67f31e1a08
Revises: ee39eac32ff8
Create Date: 2021-07-30 12:14:40.163838

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e67f31e1a08'
down_revision = 'ee39eac32ff8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('index__file_original_filename', 'file', ['original_filename'])


def downgrade():
    op.drop_index('index__file_original_filename', 'file')
