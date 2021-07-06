"""Add Temp Cloud storage fields

Revision ID: 5b9176d6cdcf
Revises: 13e0cabfe99b
Create Date: 2021-07-05 20:52:41.814985

"""
from alembic import op
import sqlalchemy as sa
from shared.database.core import MutableDict, JSONEncodedDict

# revision identifiers, used by Alembic.
revision = '5b9176d6cdcf'
down_revision = '13e0cabfe99b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('input_batch', sa.Column('upload_aws_id', sa.String))
    op.add_column('input_batch', sa.Column('upload_aws_parts_list', MutableDict.as_mutable(JSONEncodedDict)))
    op.add_column('input_batch', sa.Column('upload_azure_block_list', MutableDict.as_mutable(JSONEncodedDict)))


def downgrade():
    op.drop_column('input_batch', 'upload_aws_id')
    op.drop_column('input_batch', 'upload_aws_parts_list')
    op.drop_column('input_batch', 'upload_azure_block_list')

