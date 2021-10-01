"""Add Cuboid 3D Columns on Instance table

Revision ID: b7921392b4c3
Revises: c9dd46b1f5ff
Create Date: 2021-09-30 11:13:46.749858

"""
from alembic import op
import sqlalchemy as sa
from shared.database.core import MutableDict, JSONEncodedDict

# revision identifiers, used by Alembic.
revision = 'b7921392b4c3'
down_revision = 'c9dd46b1f5ff'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('instance', sa.Column('rotation_euler_angles', MutableDict.as_mutable(JSONEncodedDict)))
    op.add_column('instance', sa.Column('position_3d', MutableDict.as_mutable(JSONEncodedDict)))
    op.add_column('instance', sa.Column('center_3d', MutableDict.as_mutable(JSONEncodedDict)))
    op.add_column('instance', sa.Column('max_point_3d', MutableDict.as_mutable(JSONEncodedDict)))
    op.add_column('instance', sa.Column('min_point_3d', MutableDict.as_mutable(JSONEncodedDict)))
    op.add_column('instance', sa.Column('dimensions_3d', MutableDict.as_mutable(JSONEncodedDict)))


def downgrade():
    op.drop_column('instance', 'rotation_euler_angles')
    op.drop_column('instance', 'position_3d')
    op.drop_column('instance', 'center_3d')
    op.drop_column('instance', 'max_point_3d')
    op.drop_column('instance', 'min_point_3d')
    op.drop_column('instance', 'dimensions_3d')
