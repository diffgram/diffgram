"""Add PointCloud Table

Revision ID: c9dd46b1f5ff
Revises: c1e5966dc826
Create Date: 2021-09-29 08:23:10.280159

"""
from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision = 'c9dd46b1f5ff'
down_revision = '7059bb6bc019'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('point_cloud',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('original_filename', sa.String()),
                    sa.Column('description', sa.String()),
                    sa.Column('soft_delete', sa.Boolean()),
                    sa.Column('url_signed', sa.String()),
                    sa.Column('url_signed_blob_path', sa.String()),
                    sa.Column('url_signed_expiry', sa.String()),
                    sa.Column('url_signed_expiry_force_refresh', sa.String()),
                    sa.Column('service_name', sa.String()),
                    sa.Column('time_created', sa.DateTime, default = datetime.datetime.utcnow),
                    sa.Column('time_updated', sa.DateTime, onupdate = datetime.datetime.utcnow),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.add_column('file', sa.Column('point_cloud_id', sa.Integer, sa.ForeignKey('point_cloud.id')))


def downgrade():
    op.drop_column('file', 'point_cloud_id')

    op.drop_table('point_cloud')
