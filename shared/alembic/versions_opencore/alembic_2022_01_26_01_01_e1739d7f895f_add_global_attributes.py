"""add global attributes

Revision ID: e1739d7f895f
Revises: 715370463da5
Create Date: 2021-09-14 12:01:53.654617

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1739d7f895f'
down_revision = 'e3f6f51e6bd5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('attribute_template_group', 
                        sa.Column('is_global', sa.Boolean, default = False))
    op.add_column('attribute_template_group', 
                        sa.Column('global_type', sa.String, default = 'file'))

def downgrade():
    op.drop_column('attribute_template_group', 'is_global')
    op.drop_column('attribute_template_group', 'global_type')
