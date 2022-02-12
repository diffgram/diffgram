"""Rename base_class_string_column reports table

Revision ID: ddcdf79c4cbc
Revises: e25f886d921a
Create Date: 2022-02-03 13:36:24.961884

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ddcdf79c4cbc'
down_revision = 'a9023fc32298'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('report_template', 'base_class_string', new_column_name = 'item_of_interest')


def downgrade():
    op.alter_column('report_template', 'item_of_interest', new_column_name = 'base_class_string')
