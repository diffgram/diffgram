"""New File Indexes

Revision ID: 56192ed7c6cd
Revises: c6094792feeb
Create Date: 2022-09-12 18:15:34.685268

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '56192ed7c6cd'
down_revision = 'c6094792feeb'
branch_labels = None
depends_on = None


def upgrade():
    with op.get_context().autocommit_block():
        op.create_index('index_file_project_id', 'file', ['project_id'], postgresql_concurrently = True)
        op.create_index('index_file_state', 'file', ['state'], postgresql_concurrently = True)
        op.create_index('index_file_project_id_state_project_type', 'file', ['project_id', 'state', 'type'],
                        postgresql_concurrently = True)


def downgrade():
    op.drop_index('index_file_project_id', 'file')
    op.drop_index('index_file_status', 'file')
    op.drop_index('index_file_project_id_status_project_type', 'file')
