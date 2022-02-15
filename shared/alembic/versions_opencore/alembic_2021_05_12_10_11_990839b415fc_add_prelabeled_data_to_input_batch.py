"""Add Prelabeled Data to Input Batch

Revision ID: 990839b415fc
Revises: 77907aedd319
Create Date: 2021-05-12 10:11:28.285928

"""
from alembic import op
import sqlalchemy as sa
from shared.database.core import MutableDict, JSONEncodedDict
# revision identifiers, used by Alembic.
revision = '990839b415fc'
down_revision = 'c3d95120b9ce'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('input_batch', sa.Column('pre_labeled_data', MutableDict.as_mutable(JSONEncodedDict)))


def downgrade():
    op.drop_column('input_batch', 'pre_labeled_data')

