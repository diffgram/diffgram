"""Add Review Chance column to Job Table

Revision ID: 3c761954bd8d
Revises: d7a8d65bdd87
Create Date: 2021-11-09 09:59:45.767769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c761954bd8d'
down_revision = 'd7a8d65bdd87'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('job', sa.Column('review_chance', sa.Float(), default = 1.0))


def downgrade():
    op.drop_column('job', 'review_chance')
