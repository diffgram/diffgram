"""New File stats Indexes

Revision ID: 072c6491c0b5
Revises: 56192ed7c6cd
Create Date: 2022-09-14 07:10:33.268839

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '072c6491c0b5'
down_revision = '56192ed7c6cd'
branch_labels = None
depends_on = None


def upgrade():
    with op.get_context().autocommit_block():
        op.create_index('index__fa_attribute_template_id', 'file_stats', ['attribute_template_id'], postgresql_concurrently = True)
        op.create_index('index__fa_attribute_template_group_id', 'file_stats', ['attribute_template_group_id'], postgresql_concurrently = True)


def downgrade():
    op.drop_index('index__fa_attribute_template_id', 'file_stats')
    op.drop_index('index__fa_attribute_template_group_id', 'file_stats')
