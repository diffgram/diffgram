"""improve input indexes

Revision ID: 2ef6ace7da75
Revises: 2ecc88738bf4
Create Date: 2023-07-03 23:32:15.783416

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ef6ace7da75'
down_revision = '2ecc88738bf4'
branch_labels = None
depends_on = None


def upgrade():
    with op.get_context().autocommit_block():
        op.create_index('index__input_processing_deferred', 'input', ['processing_deferred'],
                        postgresql_concurrently = True)
        op.create_index('index__input_archived', 'input', ['archived'],
                        postgresql_concurrently = True)
        op.create_index('index__input_status', 'input', ['status'],
                        postgresql_concurrently = True)
        op.create_index('index__input_mode', 'input', ['mode'],
                        postgresql_concurrently = True),
        op.create_index('index__input_project_id', 'input', ['project_id'],
                        postgresql_concurrently = True)

def downgrade():
    op.drop_index('index__input_processing_deferred', 'input')
    op.drop_index('index__input_archived', 'input')
    op.drop_index('index__input_status', 'input')
    op.drop_index('index__input_mode', 'input')
    op.drop_index('index__input_project_id', 'input')
