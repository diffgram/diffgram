"""Compound files support

Revision ID: dd987ea34d75
Revises: 072c6491c0b5
Create Date: 2022-09-23 09:56:49.404342

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd987ea34d75'
down_revision = '072c6491c0b5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('file', sa.Column('ui_schema_id', sa.Integer()))
    op.create_foreign_key("ui_schema_id_fkey", "file", "ui_schema", ["ui_schema_id"], ["id"])


def downgrade():
    op.drop_column('file', 'ui_schema_id')
