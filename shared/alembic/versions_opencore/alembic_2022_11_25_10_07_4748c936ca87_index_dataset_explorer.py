"""Index dataset explorer

Revision ID: 4748c936ca87
Revises: 25580ca9875a
Create Date: 2022-11-25 10:07:58.317453

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '4748c936ca87'
down_revision = '25580ca9875a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('index__project_id_parent_id_type', 'file', ['project_id', 'state', 'type', 'parent_id'])
    op.create_index(
        'index__parent_files',
        'file',
        ['project_id', 'parent_id'],
        postgresql_where = text("file.parent_id IS NOT Null"))


def downgrade():
    op.drop_index('index__project_id_parent_id_type', 'file')
    op.drop_index('index__parent_files', 'file')
