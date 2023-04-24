"""Add new UI Schema custom buttons

Revision ID: 3dda228d38f0
Revises: 7c18149a20c8
Create Date: 2023-04-20 16:22:40.027501

"""
from alembic import op
import sqlalchemy as sa
from shared.database.core import MutableDict
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = '3dda228d38f0'
down_revision = '7c18149a20c8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ui_schema', sa.Column('custom_buttons', MutableDict.as_mutable(JSONB)))


def downgrade():
    op.drop_column('ui_schema', 'custom_buttons')