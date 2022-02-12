"""Add Time Tracking to UI Schema

Revision ID: 4b2b0450b93b
Revises: ddcdf79c4cbc
Create Date: 2022-02-09 10:26:27.161148

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects.postgresql import JSONB
from shared.database.core import MutableDict

# revision identifiers, used by Alembic.
revision = '4b2b0450b93b'
down_revision = 'ddcdf79c4cbc'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ui_schema', sa.Column('time_tracking', MutableDict.as_mutable(JSONB)))


def downgrade():
    op.drop_column('ui_schema', 'time_tracking')
