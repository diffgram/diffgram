"""Schema to Migration

Revision ID: 501d8176d48f
Revises: 3feda3d442be
Create Date: 2022-06-01 14:37:25.346216

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '501d8176d48f'
down_revision = '3feda3d442be'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('project_migration', sa.Column('label_schema_id', sa.Integer, sa.ForeignKey('label_schema.id')))
    op.add_column('label_schema', sa.Column('is_default', sa.Boolean), default = False)


def downgrade():
    op.drop_column('project_migration', sa.Column('label_schema_id', sa.Integer, sa.ForeignKey('label_schema.id')))
    op.drop_column('label_schema', sa.Column('is_default', sa.Boolean))
