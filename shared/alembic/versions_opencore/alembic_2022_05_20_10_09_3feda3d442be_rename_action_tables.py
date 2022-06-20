"""Rename Action Tables

Revision ID: 3feda3d442be
Revises: cf7e13f71c9d
Create Date: 2022-04-20 10:09:05.710726

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from shared.database.action.action_template import Action_Template
from shared.database.action.action import Action
from shared.database.action.workflow import Workflow
from shared.database.event.event import Event
from shared.database.core import MutableDict, JSONEncodedDict
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = '3feda3d442be'
down_revision = 'ee1f8ffb8c4d'
branch_labels = None
depends_on = None


def create_default_action_templates(session):
    Action_Template.new(
        session = session,
        public_name = 'Human Labeling Task',
        description = 'Add tasks to a task template',
        icon = 'https://www.svgrepo.com/show/376121/list-task.svg',
        kind = 'create_task',
        category = None,
        trigger_data = {'trigger_event_name': 'input_file_uploaded'},
        condition_data = {'event_name': None},
        completion_condition_data = {'event_name': 'task_completed'},
    )
    Action_Template.new(
        session = session,
        public_name = 'JSON Export',
        description = 'Generate JSON Export',
        icon = 'https://www.svgrepo.com/show/46774/export.svg',
        kind = 'export',
        category = None,
        trigger_data = {'trigger_event_name': 'task_completed'},
        condition_data = {'event_name': 'all_tasks_completed'},
        completion_condition_data = {'event_name': 'export_generate_success'},
    )


def upgrade():
    op.rename_table('action_flow', 'workflow')
    op.rename_table('action_flow_event', 'workflow_run')
    op.rename_table('action_event', 'action_run')
    op.rename_table('action_flow_trigger_event_queue', 'workflow_trigger_event_queue')

    op.alter_column('action', 'flow_id', new_column_name = 'workflow_id')
    op.alter_column('action_run', 'flow_id', new_column_name = 'workflow_id')
    op.alter_column('workflow_trigger_event_queue', 'action_flow_id', new_column_name = 'workflow_id')
    op.alter_column('action_run', 'flow_event_id', new_column_name = 'workflow_run_id')
    op.alter_column('workflow_run', 'flow_id', new_column_name = 'workflow_id')

    op.add_column('action_template', sa.Column('icon', sa.String, default = ''))
    op.add_column('action_template', sa.Column('description', sa.String, default = ''))
    op.add_column('action_template', sa.Column('trigger_data', MutableDict.as_mutable(JSONB)))
    op.add_column('action_template', sa.Column('condition_data', MutableDict.as_mutable(JSONB)))
    op.add_column('action_template', sa.Column('completion_condition_data', MutableDict.as_mutable(JSONB)))
    op.add_column('action_template', sa.Column('is_global', sa.Boolean, default = True))

    op.add_column('action', sa.Column('icon', sa.String, default = ''))
    op.add_column('action', sa.Column('description', sa.String, default = ''))
    op.add_column('action', sa.Column('trigger_data', MutableDict.as_mutable(JSONB)))
    op.add_column('action', sa.Column('config_data', MutableDict.as_mutable(JSONB)))
    op.add_column('action', sa.Column('condition_data', MutableDict.as_mutable(JSONB)))
    op.add_column('action', sa.Column('completion_condition_data', MutableDict.as_mutable(JSONB)))
    op.add_column('action', sa.Column('public_name',  sa.String, default = ''))
    op.add_column('action', sa.Column('ordinal',  sa.Integer))

    # We need to remove old default action templates. Since now we'll init them with new values
    bind = op.get_bind()
    session = orm.Session(bind = bind)
    result = session.query(Action_Template).filter(
        Action_Template.kind.in_([
            'count',
            'delay',
            'condition',
            'email',
            'webhook'
        ])
    ).all()

    for temp in result:
        actions = session.query(Action).filter(
            Action.template_id == temp.id
        ).all()
        for act in actions:
            act.template_id = None
            session.add(act)
        session.delete(temp)

    create_default_action_templates(session)

    op.add_column('event', sa.Column('action_id', sa.Integer(), sa.ForeignKey('action.id')))
    op.add_column('event', sa.Column('workflow_id', sa.Integer(), sa.ForeignKey('workflow.id')))
    op.add_column('event', sa.Column('directory_id', sa.Integer(), sa.ForeignKey('working_dir.id')))


def downgrade():
    op.drop_column('event', 'action_id')
    op.drop_column('event', 'workflow_id')
    op.drop_column('event', 'directory_id')

    bind = op.get_bind()
    session = orm.Session(bind = bind)
    actions = session.query(Action).update({Action.template_id: None}, synchronize_session = False)
    result = session.query(Action_Template).filter(
        Action_Template.kind.in_([
            'create_task',
            'export',
        ])
    ).all()

    for temp in result:
        session.add(temp)
        session.delete(temp)
    session.commit()
    op.rename_table('workflow', 'action_flow')
    op.rename_table('workflow_run', 'action_flow_event')
    op.rename_table('action_run', 'action_event')
    op.rename_table('workflow_trigger_event_queue', 'action_flow_trigger_event_queue')

    op.alter_column('action', 'workflow_id', new_column_name = 'flow_id')
    op.alter_column('action_event', 'workflow_id', new_column_name = 'flow_id')
    op.alter_column('action_event', 'workflow_run_id', new_column_name = 'flow_event_id')
    op.alter_column('action_flow_event', 'workflow_id', new_column_name = 'flow_id')
    op.alter_column('action_flow_trigger_event_queue', 'workflow_id', new_column_name = 'action_flow_id')
    op.drop_column('action_template', 'icon')
    op.drop_column('action_template', 'description')
    op.drop_column('action_template', 'trigger_data')
    op.drop_column('action_template', 'condition_data')
    op.drop_column('action_template', 'completion_condition_data')
    op.drop_column('action_template', 'is_global')

    op.drop_column('action', 'icon')
    op.drop_column('action', 'description')
    op.drop_column('action', 'trigger_data')
    op.drop_column('action', 'config_data')
    op.drop_column('action', 'condition_data')
    op.drop_column('action', 'completion_condition_data')
    op.drop_column('action', 'public_name')
    op.drop_column('action', 'ordinal')
