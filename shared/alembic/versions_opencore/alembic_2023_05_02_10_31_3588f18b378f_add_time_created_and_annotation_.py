"""Add Time created and annotation complete indexes

Revision ID: 3588f18b378f
Revises: 9cfc913ef62d
Create Date: 2023-05-02 10:31:12.218243

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3588f18b378f'
down_revision = '9cfc913ef62d'
branch_labels = None
depends_on = None



def upgrade():
    with op.get_context().autocommit_block():
        op.create_index('index_project_created_time', 'file',
                        ['project_id', 'created_time'],
                        postgresql_concurrently = True)
        op.create_index('index_project_ann_is_complete', 'file',
                        ['project_id', 'ann_is_complete'],
                        postgresql_concurrently = True)


def downgrade():
    op.drop_index('index_project_created_time', 'file')
    op.drop_index('index_project_ann_is_complete', 'file')
