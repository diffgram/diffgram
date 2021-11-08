"""Add Relation type to User_To_Job Table

Revision ID: d7a8d65bdd87
Revises: 32dbb3259c2b
Create Date: 2021-11-08 09:39:00.058143

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7a8d65bdd87'
down_revision = '32dbb3259c2b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user_to_job', sa.Column('relation', sa.String(), default = False))


def downgrade():
    op.drop_column('user_to_job', 'relation')
