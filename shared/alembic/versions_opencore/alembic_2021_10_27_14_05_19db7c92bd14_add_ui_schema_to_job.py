"""Add UI Schema to Job

Revision ID: 19db7c92bd14
Revises: 2f5a1ceb7fc9
Create Date: 2021-10-27 14:05:52.430267

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '19db7c92bd14'
down_revision = '2f5a1ceb7fc9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('job', sa.Column('ui_schema_id', sa.Integer))
    op.create_foreign_key("ui_schema_id_fk", "job", "ui_schema", ["ui_schema_id"], ["id"])


def downgrade():
    op.drop_column('job', 'ui_schema_id')

