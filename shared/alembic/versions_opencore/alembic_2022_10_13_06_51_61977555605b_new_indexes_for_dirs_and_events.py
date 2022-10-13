"""New Indexes for Dirs and Events

Revision ID: 61977555605b
Revises: 072c6491c0b5
Create Date: 2022-10-13 06:51:09.963573

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '61977555605b'
down_revision = '072c6491c0b5'
branch_labels = None
depends_on = None


def upgrade():
    with op.get_context().autocommit_block():
        op.create_index('index__project_directory_list_project', 'project_directory_list', ['project_id'],
                        postgresql_concurrently = True)
        op.create_index('index__project_directory_list_dir', 'project_directory_list', ['working_dir_id'],
                        postgresql_concurrently = True)
        op.create_index('index__project_directory_dir_nickname', 'project_directory_list', ['project_id', 'working_dir_id', 'nickname'],
                        postgresql_concurrently = True)


def downgrade():
    op.drop_index('index__project_directory_list_project', 'project_directory_list')
    op.drop_index('index__project_directory_list_dir', 'project_directory_list')
    op.drop_index('index__project_directory_dir_nickname', 'project_directory_list')
