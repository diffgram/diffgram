"""Dataset Tags

Revision ID: f098a0aa6959
Revises: ed8dea09f743
Create Date: 2022-08-04 16:40:21.674510

"""
from alembic import op
import sqlalchemy as sa
import datetime


# revision identifiers, used by Alembic.
revision = 'f098a0aa6959'
down_revision = 'ed8dea09f743'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('dataset_tag',
        sa.Column('dataset_id', sa.Integer(), nullable = False, primary_key = True),
        sa.Column('tag_id', sa.Integer(), nullable = False, primary_key = True),
        sa.Column('project_id', sa.Integer(), nullable = False, primary_key = True),
        sa.Column('time_created', sa.DateTime(), default = datetime.datetime.utcnow)
    )


def downgrade():
    op.drop_table('dataset_tag')
