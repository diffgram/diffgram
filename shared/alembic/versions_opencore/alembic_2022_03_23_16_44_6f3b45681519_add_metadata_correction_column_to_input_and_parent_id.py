"""Add Metadata correction column to input and parent id

Revision ID: 6f3b45681519
Revises: a0a5666b5fbf
Create Date: 2022-03-23 16:44:01.593997

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f3b45681519'
down_revision = 'a0a5666b5fbf'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('input', sa.Column('auto_correct_instances_from_image_metadata', sa.Boolean(), default = False))
    op.add_column('attribute_template', sa.Column('parent_id', sa.Integer, sa.ForeignKey('attribute_template.id')))


def downgrade():
    op.drop_column('input', 'auto_correct_instances_from_image_metadata')
    op.drop_column('attribute_template', 'parent_id')
