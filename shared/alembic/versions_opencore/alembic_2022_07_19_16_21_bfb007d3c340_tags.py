"""tags

Revision ID: bfb007d3c340
Revises: 625370e1484b
Create Date: 2022-07-19 16:21:55.940920

"""
from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision = 'bfb007d3c340'
down_revision = '625370e1484b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('job_tag',
        sa.Column('job_id', sa.Integer(), nullable = False, primary_key = True),
        sa.Column('tag_id', sa.Integer(), nullable = False, primary_key = True),
        sa.Column('project_id', sa.Integer(), nullable = False, primary_key = True),
        sa.Column('time_created', sa.DateTime(), default = datetime.datetime.utcnow)
    )

    op.add_column('tag', sa.Column('project_id', sa.Integer()))
    op.add_column('tag', sa.Column('archived', sa.Boolean()))
    op.add_column('tag', sa.Column('color_hex', sa.String()))
    op.add_column('tag', sa.Column('time_created', sa.DateTime(), default=datetime.datetime.utcnow))
    op.add_column('tag', sa.Column('time_updated', sa.DateTime(), onupdate=datetime.datetime.utcnow))

    op.create_foreign_key("tag_project_id_fkey", "tag", "project", ["project_id"], ["id"])


def downgrade():

    op.drop_table('job_tag')

    op.drop_column('tag', 'project_id')
    op.drop_column('tag', 'archived')
    op.drop_column('tag', 'color_hex')
    op.drop_column('tag', 'time_created')
    op.drop_column('tag', 'time_updated')