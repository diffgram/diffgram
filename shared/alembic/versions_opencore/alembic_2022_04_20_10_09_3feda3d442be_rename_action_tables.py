"""Rename Action Tables

Revision ID: 3feda3d442be
Revises: cf7e13f71c9d
Create Date: 2022-04-20 10:09:05.710726

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3feda3d442be'
down_revision = 'cf7e13f71c9d'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('action_flow', 'workflow')
    op.rename_table('action_flow_event', 'workflow_run')
    op.rename_table('action_event', 'action_run')
    op.rename_table('action_flow_trigger_event_queue', 'workflow_trigger_event_queue')

    op.alter_column('action', 'flow_id', new_column_name = 'workflow_id')
    op.alter_column('action_run', 'flow_id', new_column_name = 'workflow_id')
    op.alter_column('action_run', 'flow_event_id', new_column_name = 'workflow_run_id')
    op.alter_column('workflow_run', 'flow_id', new_column_name = 'workflow_id')


def downgrade():
    op.rename_table('workflow', 'action_flow')
    op.rename_table('workflow_run', 'action_flow_event')
    op.rename_table('action_run', 'action_event')
    op.rename_table('workflow_trigger_event_queue', 'action_flow_trigger_event_queue')

    op.alter_column('action', 'workflow_id', new_column_name = 'flow_id')
    op.alter_column('action_event', 'workflow_id', new_column_name = 'flow_id')
    op.alter_column('action_event', 'workflow_run_id', new_column_name = 'flow_event_id')
    op.alter_column('action_flow_event', 'workflow_id', new_column_name = 'flow_id')
