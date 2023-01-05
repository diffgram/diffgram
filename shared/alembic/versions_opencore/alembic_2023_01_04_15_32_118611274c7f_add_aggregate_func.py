"""add aggregate_func'

Revision ID: 118611274c7f
Revises: 8c27f0ff4da8
Create Date: 2023-01-04 15:32:05.282044

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '118611274c7f'
down_revision = '8c27f0ff4da8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('report_template', 
                  sa.Column('aggregate_func', sa.String()))

def downgrade():
    op.drop_column('report_template', 'aggregate_func')