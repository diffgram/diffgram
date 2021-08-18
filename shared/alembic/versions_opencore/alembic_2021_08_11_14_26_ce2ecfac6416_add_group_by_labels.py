"""Add Group By Labels

Revision ID: ce2ecfac6416
Revises: 3e67f31e1a08
Create Date: 2021-08-11 14:26:40.300824

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce2ecfac6416'
down_revision = '3e67f31e1a08'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('report_template', sa.Column('group_by_labels', sa.Boolean, default = False))


def downgrade():
    op.drop_column('report_template', 'group_by_labels')
