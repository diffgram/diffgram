"""Add Geospatial Tables and Columns

Revision ID: e7d84ad133ea
Revises: 6f3b45681519
Create Date: 2022-04-21 11:10:24.140492

"""
from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision = 'e7d84ad133ea'
down_revision = 'cf7e13f71c9d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('geo_asset',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('original_filename', sa.String()),
                    sa.Column('description', sa.String()),
                    sa.Column('soft_delete', sa.Boolean()),
                    sa.Column('url_signed', sa.String()),
                    sa.Column('type', sa.String()),
                    sa.Column('url_signed_blob_path', sa.String()),
                    sa.Column('url_signed_expiry', sa.String()),
                    sa.Column('file_id', sa.Integer(), ),
                    sa.Column('project_id', sa.Integer(), ),
                    sa.Column('url_signed_expiry_force_refresh', sa.String()),
                    sa.Column('service_name', sa.String()),
                    sa.Column('time_created', sa.DateTime, default = datetime.datetime.utcnow),
                    sa.Column('time_updated', sa.DateTime, onupdate = datetime.datetime.utcnow),
                    sa.PrimaryKeyConstraint('id'),
                    sa.ForeignKeyConstraint(['file_id'], ['file.id'], ),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
                    )

    op.add_column('instance', sa.Column('lonlat', sa.ARRAY(sa.Float), nullable = True))
    op.add_column('instance', sa.Column('coords', sa.ARRAY(sa.Float), nullable = True))
    op.add_column('instance', sa.Column('radius', sa.Float, nullable = True))
    op.add_column('instance', sa.Column('bounds', sa.ARRAY(sa.Float), nullable = True))
    op.add_column('instance', sa.Column('bounds_lonlat', sa.ARRAY(sa.Float), nullable = True))

    op.create_index('index__geo_asset_project_id', 'geo_asset', ['project_id'])
    op.create_index('index__geo_asset_file_id', 'geo_asset', ['file_id'])
    op.create_index('index__geo_asset_project_file', 'geo_asset', ['project_id', 'file_id'])

def downgrade():
    op.drop_index('index__geo_asset_project_id')
    op.drop_index('index__geo_asset_file_id')
    op.drop_index('index__geo_asset_project_file')
    op.drop_column('instance', 'lonlat')
    op.drop_column('instance', 'coords')
    op.drop_column('instance', 'radius')
    op.drop_column('instance', 'bounds')
    op.drop_column('instance', 'bounds_lonlat')
    op.drop_table('geo_asset')
