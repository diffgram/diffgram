"""Add workflow and action trigger to input table.

Revision ID: 2ecc88738bf4
Revises: 7f4a21af81ab
Create Date: 2023-05-18 09:26:21.324633

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ecc88738bf4'
down_revision = '7f4a21af81ab'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('input', sa.Column('workflow_trigger_id', sa.Integer, sa.ForeignKey('workflow.id')))
    op.add_column('input', sa.Column('action_trigger_id', sa.Integer, sa.ForeignKey('action.id')))


def downgrade():
    op.drop_column('input', 'workflow_trigger_id')
    op.drop_column('input', 'action_trigger_id')
