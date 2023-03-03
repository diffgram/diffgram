"""Add index to the job table

Revision ID: f1b006dd9e9e
Revises: 61977555605b
Create Date: 2022-11-15 12:24:30.640669

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1b006dd9e9e'
down_revision = '61977555605b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('index__job_project_id', 'job', ['project_id', 'status'])



def downgrade():
    op.drop_index('index__job_project_id', 'job')
