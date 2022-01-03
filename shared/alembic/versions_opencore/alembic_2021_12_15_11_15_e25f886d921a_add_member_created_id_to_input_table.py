"""Add Member created ID To Input Table

Revision ID: e25f886d921a
Revises: b7921392b4c3
Create Date: 2021-12-15 11:15:10.264045

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e25f886d921a'
down_revision = 'efd1cf42073a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('input', sa.Column('member_created_id', sa.Integer(), nullable = True))
    op.add_column('input', sa.Column('member_updated_id', sa.Integer(), nullable = True))


def downgrade():
    op.drop_column('input', 'member_created_id')
    op.drop_column('input', 'member_updated_id')
