"""Add Download Status on Batch

Revision ID: 7ff038954a96
Revises: 9192f806a8cb
Create Date: 2021-07-21 13:27:49.097582

"""
from alembic import op
import sqlalchemy as sa
from shared.database.core import MutableDict, JSONEncodedDict


# revision identifiers, used by Alembic.
revision = '7ff038954a96'
down_revision = '9192f806a8cb'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('input_batch', sa.Column('download_status_pre_labeled_data', sa.String))
    op.add_column('input_batch', sa.Column('download_log_pre_labeled_data', MutableDict.as_mutable(JSONEncodedDict)))


def downgrade():
    op.drop_column('input_batch', 'download_status_pre_labeled_data')
    op.drop_column('input_batch', 'download_log_pre_labeled_data')
