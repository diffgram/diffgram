"""Add Relations to Instance

Revision ID: e3f6f51e6bd5
Revises: e18fd230021b
Create Date: 2022-01-24 12:35:43.702355

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3f6f51e6bd5'
down_revision = '8736666d667d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('instance', sa.Column('from_instance_id', sa.Integer, sa.ForeignKey('instance.id'), nullable = True))
    op.add_column('instance', sa.Column('to_instance_id', sa.Integer, sa.ForeignKey('instance.id'), nullable = True))


def downgrade():
    op.drop_column('instance', 'from_instance_id')
    op.drop_column('instance', 'to_instance_id')
