"""Add Unique Together to Frame numbers

Revision ID: 9192f806a8cb
Revises: 5b9176d6cdcf
Create Date: 2021-07-09 08:38:47.670954

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9192f806a8cb'
down_revision = '5b9176d6cdcf'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint('unique_frame_number', 'file', ['video_parent_file_id', 'frame_number'])


def downgrade():
    op.drop_constraint('unique_frame_number', 'file')
