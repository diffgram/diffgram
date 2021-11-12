"""Add Action Tables

Revision ID: 3c50e7d2bb18
Revises: 53bdf159858b
Create Date: 2021-11-11 09:25:26.815675

"""
from alembic import op
import sqlalchemy as sa
from shared.database_setup_supporting import *
# revision identifiers, used by Alembic.
revision = '3c50e7d2bb18'
down_revision = '53bdf159858b'
branch_labels = None
depends_on = None





def upgrade():
    action_template = op.create_table('action_template',
                                      sa.Column('id', sa.Integer(), nullable = False),
                                      sa.Column('public_name', sa.String(), nullable = True),
                                      sa.Column('kind', sa.String(), nullable = True),
                                      sa.Column('category', sa.String(), nullable = True),
                                      sa.Column('is_available', sa.Boolean(), nullable = True),
                                      sa.Column('member_created_id', sa.Integer(), nullable = True),
                                      sa.Column('member_updated_id', sa.Integer(), nullable = True),
                                      sa.Column('time_created', sa.DateTime(), nullable = True),
                                      sa.Column('time_updated', sa.DateTime(), nullable = True),
                                      sa.PrimaryKeyConstraint('id')
                                      )

    op.create_table('action_flow',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('name', sa.String(), nullable = True),
                    sa.Column('string_id', sa.String(), nullable = True),
                    sa.Column('trigger_type', sa.String()),
                    sa.Column('time_window', sa.String()),
                    sa.Column('active', sa.Boolean(), nullable = True),
                    sa.Column('archived', sa.Boolean(), nullable = True),
                    sa.Column('is_new', sa.Boolean(), nullable = True),
                    sa.Column('kind', sa.String(), nullable = True),
                    sa.Column('count_events', sa.Integer(), nullable = True),
                    sa.Column('directory_id', sa.Integer(), nullable = True),
                    sa.Column('first_action_id', sa.BIGINT(), nullable = True),
                    sa.Column('last_action_id', sa.BIGINT(), nullable = True),
                    sa.Column('project_id', sa.Integer(), nullable = True),
                    sa.Column('org_id', sa.Integer(), nullable = True),
                    sa.Column('member_created_id', sa.Integer(), nullable = True),
                    sa.Column('member_updated_id', sa.Integer(), nullable = True),
                    sa.Column('time_created', sa.DateTime(), nullable = True),
                    sa.Column('time_updated', sa.DateTime(), nullable = True),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('action_flow_event',
                    sa.Column('id', sa.BIGINT(), nullable = False),
                    sa.Column('status', sa.String(), nullable = True),
                    sa.Column('status_description', sa.String(), nullable = True),
                    sa.Column('file_id', sa.BIGINT(), nullable = True),
                    sa.Column('flow_id', sa.Integer(), nullable = True),
                    sa.Column('project_id', sa.Integer(), nullable = True),
                    sa.Column('org_id', sa.Integer(), nullable = True),
                    sa.Column('time_created', sa.DateTime(), nullable = True),
                    sa.Column('time_updated', sa.DateTime(), nullable = True),
                    sa.Column('link_to_results', sa.String(), nullable = True),
                    sa.ForeignKeyConstraint(['file_id'], ['file.id'], ),
                    sa.ForeignKeyConstraint(['flow_id'], ['action_flow.id'], ),
                    sa.ForeignKeyConstraint(['org_id'], ['org.id'], ),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('action',
                    sa.Column('id', sa.BIGINT(), nullable = False),
                    sa.Column('kind', sa.String(), nullable = True),
                    sa.Column('active', sa.Boolean(), nullable = True),
                    sa.Column('archived', sa.Boolean(), nullable = True),
                    sa.Column('status', sa.String(), nullable = True),
                    sa.Column('template_id', sa.Integer(), nullable = True),
                    sa.Column('flow_id', sa.Integer(), nullable = True),
                    sa.Column('is_root', sa.Boolean(), nullable = True),
                    sa.Column('root_id', sa.Integer(), nullable = True),
                    sa.Column('parent_id', sa.Integer(), nullable = True),
                    sa.Column('child_primary_id', sa.Integer(), nullable = True),
                    sa.Column('project_id', sa.Integer(), nullable = True),
                    sa.Column('org_id', sa.Integer(), nullable = True),
                    sa.Column('member_created_id', sa.Integer(), nullable = True),
                    sa.Column('member_updated_id', sa.Integer(), nullable = True),
                    sa.Column('time_created', sa.DateTime(), nullable = True),
                    sa.Column('time_updated', sa.DateTime(), nullable = True),
                    sa.Column('brain_kind', sa.String(), nullable = True),
                    sa.Column('brain_run_visual', sa.Boolean(), nullable = True),
                    sa.Column('brain_completion_directory_id', sa.Integer(), nullable = True),
                    sa.Column('count_label_file_id', sa.Integer(), nullable = True),
                    sa.Column('count', sa.Integer(), nullable = True),
                    sa.Column('count_confidence_threshold', sa.Float(), nullable = True),
                    sa.Column('condition_operator', sa.String(), nullable = True),
                    sa.Column('condition_left_operand', sa.String(), nullable = True),
                    sa.Column('condition_right_operand', sa.String(), nullable = True),
                    sa.Column('condition_true_exists', sa.Boolean(), nullable = True),
                    sa.Column('condition_false_exists', sa.Boolean(), nullable = True),
                    sa.Column('condition_true_action_id', sa.Integer(), nullable = True),
                    sa.Column('condition_false_action_id', sa.Integer(), nullable = True),
                    sa.Column('time_delay', sa.Integer(), nullable = True),
                    sa.Column('email_send_to', sa.String(), nullable = True),
                    sa.Column('email_subject', sa.String(), nullable = True),
                    sa.Column('email_body', sa.String(), nullable = True),
                    sa.Column('overlay_kind', sa.String(), nullable = True),
                    sa.Column('overlay_text', sa.String(), nullable = True),
                    sa.Column('overlay_image_id', sa.Integer(), nullable = True),
                    sa.Column('overlay_position', sa.String(), nullable = True),
                    sa.Column('overlay_size', sa.String(), nullable = True),
                    sa.Column('overlay_label_file_id', sa.Integer(), nullable = True),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.add_column('action', sa.Column('url_to_post', sa.String()))
    op.add_column('action', sa.Column('secret_webhook', sa.String()))

    op.create_table('action_event',
                    sa.Column('id', sa.BIGINT(), nullable = False),
                    sa.Column('flow_event_id', sa.BIGINT(), nullable = True),
                    sa.Column('file_id', sa.BIGINT(), nullable = True),
                    sa.Column('action_id', sa.BIGINT(), nullable = True),
                    sa.Column('kind', sa.String(), nullable = True),
                    sa.Column('flow_id', sa.Integer(), nullable = True),
                    sa.Column('project_id', sa.Integer(), nullable = True),
                    sa.Column('org_id', sa.Integer(), nullable = True),
                    sa.Column('time_created', sa.DateTime(), nullable = True),
                    sa.Column('time_updated', sa.DateTime(), nullable = True),
                    sa.Column('link_to_results', sa.String(), nullable = True),
                    sa.Column('count', sa.Integer(), nullable = True),
                    sa.Column('condition_true', sa.Boolean(), nullable = True),
                    sa.Column('condition_false', sa.Boolean(), nullable = True),
                    sa.Column('condition_result', sa.Boolean(), nullable = True),
                    sa.Column('email_was_sent_to', sa.String(), nullable = True),
                    sa.Column('email_subject', sa.String(), nullable = True),
                    sa.Column('email_body', sa.String(), nullable = True),
                    sa.Column('overlay_rendered_image_id', sa.Integer(), nullable = True),
                    sa.ForeignKeyConstraint(['action_id'], ['action.id'], ),
                    sa.ForeignKeyConstraint(['file_id'], ['file.id'], ),
                    sa.ForeignKeyConstraint(['flow_event_id'], ['action_flow_event.id'], ),
                    sa.ForeignKeyConstraint(['flow_id'], ['action_flow.id'], ),
                    sa.ForeignKeyConstraint(['org_id'], ['org.id'], ),
                    sa.ForeignKeyConstraint(['overlay_rendered_image_id'], ['image.id'], ),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('action_flow_trigger_event_queue',
                    sa.Column('id', sa.BIGINT, nullable = False, primary_key = True),
                    sa.Column('type', sa.String(), nullable = True),
                    sa.Column('input_id', sa.Integer(), nullable = True),
                    sa.Column('has_aggregation_event_running', sa.Boolean(), nullable = True, default = None),
                    sa.Column('aggregation_window_start_time', sa.DateTime(), nullable = True),
                    sa.Column('project_id', sa.Integer(), nullable = True),
                    sa.Column('task_id', sa.Integer(), nullable = True),
                    sa.Column('job_id', sa.Integer(), nullable = True),
                    sa.Column('action_flow_id', sa.Integer(), nullable = True),
                    sa.Column('org_id', sa.Integer(), nullable = True),
                    sa.Column('time_created', sa.DateTime(), nullable = True),
                    sa.Column('time_updated', sa.DateTime(), nullable = True),
                    sa.Column('member_created_id', sa.Integer(), nullable = True),
                    sa.Column('member_updated_id', sa.Integer(), nullable = True),

                    )
    op.create_unique_constraint('unique_aggregation_event', 'action_flow_trigger_event_queue',
                                ['action_flow_id', 'has_aggregation_event_running'])
    op.create_foreign_key("input_id_fkey", "action_flow_trigger_event_queue", "input", ["input_id"], ["id"])
    op.create_foreign_key("project_id_fkey", "action_flow_trigger_event_queue", "project", ["project_id"], ["id"])
    op.create_foreign_key("task_id_fkey", "action_flow_trigger_event_queue", "task", ["task_id"], ["id"])
    op.create_foreign_key("job_id_fkey", "action_flow_trigger_event_queue", "task", ["job_id"], ["id"])
    op.create_foreign_key("action_flow_id_fkey", "action_flow_trigger_event_queue", "action_flow", ["action_flow_id"],
                          ["id"])
    op.create_foreign_key("org_id_fkey", "action_flow_trigger_event_queue", "org", ["org_id"], ["id"])

    op.create_foreign_key("action_template_id_fkey", "action", "action_template", ["template_id"], ["id"])
    op.create_foreign_key("action_template_member_created_id_fkey", "action_template", "member", ["member_created_id"],
                          ["id"])
    op.create_foreign_key("action_template_member_updated_id_fkey", "action_template", "member", ["member_updated_id"],
                          ["id"])


def downgrade():
    op.drop_constraint('input_id_fkey', 'action_flow_trigger_event_queue', type_ = 'foreignkey')
    op.drop_constraint('project_id_fkey', 'action_flow_trigger_event_queue', type_ = 'foreignkey')
    op.drop_constraint('task_id_fkey', 'action_flow_trigger_event_queue', type_ = 'foreignkey')
    op.drop_constraint('job_id_fkey', 'action_flow_trigger_event_queue', type_ = 'foreignkey')
    op.drop_constraint('action_flow_id_fkey', 'action_flow_trigger_event_queue', type_ = 'foreignkey')
    op.drop_constraint('org_id_fkey', 'action_flow_trigger_event_queue', type_ = 'foreignkey')
    op.drop_constraint('action_template_id_fkey', 'action', type_ = 'foreignkey')
    op.drop_constraint('action_template_member_created_id_fkey', 'action_template', type_ = 'foreignkey')
    op.drop_constraint('action_template_member_updated_id_fkey', 'action_template', type_ = 'foreignkey')

    op.drop_table('action_flow_trigger_event_queue')

    op.drop_table('action_event')
    op.drop_table('action')
    op.drop_table('action_flow_event')
    op.drop_table('action_flow')
    op.drop_table('action_template')
