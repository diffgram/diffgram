"""Add Status Filter to Reports

Revision ID: 3bfaee3a81b3
Revises: 4748c936ca87
Create Date: 2022-12-07 14:26:32.314507

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3bfaee3a81b3'
down_revision = '4748c936ca87'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('report_template', sa.Column('task_event_type', sa.String()))


def downgrade():
    op.drop_column('report_template', 'task_event_type')
