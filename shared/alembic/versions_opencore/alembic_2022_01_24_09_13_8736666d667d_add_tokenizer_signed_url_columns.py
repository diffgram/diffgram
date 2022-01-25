"""Add Tokenizer Signed URL Columns

Revision ID: 8736666d667d
Revises: e18fd230021b
Create Date: 2022-01-24 09:13:24.147953

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8736666d667d'
down_revision = 'e18fd230021b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('text_file', sa.Column('tokens_url_signed', sa.String, default = 'wink'))
    op.add_column('text_file', sa.Column('tokens_url_signed_blob_path', sa.String, default = 'wink'))
    op.add_column('text_file', sa.Column('tokens_url_signed_expiry', sa.String, default = 'wink'))


def downgrade():
    op.drop_column('text_file', 'tokens_url_signed')
    op.drop_column('text_file', 'tokens_url_signed_blob_path')
    op.drop_column('text_file', 'tokens_url_signed_expiry')
