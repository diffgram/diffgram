"""report_add_second_group_by

Revision ID: a576f5a04c03
Revises: 3bfaee3a81b3
Create Date: 2022-12-28 13:51:00.991936

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a576f5a04c03'
down_revision = '3bfaee3a81b3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('report_template', sa.Column('second_group_by', sa.String()))


def downgrade():
    op.drop_column('report_template', 'second_group_by')

