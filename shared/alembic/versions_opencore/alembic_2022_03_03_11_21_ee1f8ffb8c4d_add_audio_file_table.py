"""Add Audio File Table

Revision ID: ee1f8ffb8c4d
Revises: 0e90db072b0b
Create Date: 2022-03-03 11:21:29.142649

"""
from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision = 'ee1f8ffb8c4d'
down_revision = '0e90db072b0b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('audio_file',
                    sa.Column('id', sa.BIGINT, nullable = False, primary_key = True),
                    sa.Column('original_filename', sa.String()),
                    sa.Column('description', sa.String()),
                    sa.Column('soft_delete', sa.Boolean(), default = False),
                    sa.Column('url_public', sa.String()),
                    sa.Column('url_signed', sa.String()),
                    sa.Column('url_signed_blob_path', sa.String()),
                    sa.Column('url_signed_expiry', sa.Integer()),
                    sa.Column('url_signed_expiry_force_refresh', sa.Integer()),
                    sa.Column('time_created', sa.DateTime(), default = datetime.datetime.utcnow),
                    sa.Column('time_updated', sa.DateTime(), onupdate = datetime.datetime.utcnow))


def downgrade():
    op.drop_table('audio_file')

