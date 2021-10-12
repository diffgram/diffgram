"""Add UI Schema

Revision ID: bdcd484ece5f
Revises: c1e5966dc826
Create Date: 2021-10-12 00:14:52.866342

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
import datetime

# revision identifiers, used by Alembic.
revision = 'bdcd484ece5f'
down_revision = 'c1e5966dc826'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('ui_schema',
        sa.Column('id', sa.BIGINT, nullable = False, primary_key = True),
        sa.Column('name', sa.String()),
        sa.Column('note', sa.String()),
        sa.Column('version', sa.Integer(), default = 0),

        sa.Column('created_time', sa.DateTime(), default = datetime.datetime.utcnow),
        sa.Column('last_updated_time', sa.DateTime(), onupdate = datetime.datetime.utcnow),
       
        sa.Column('client_created_time', sa.DateTime(), nullable = True),
        sa.Column('creation_ref_id', sa.String()),

        sa.Column('deleted_time', sa.DateTime(), nullable = True),
       
        sa.Column('member_created_id', sa.Integer()),
        sa.Column('member_updated_id', sa.Integer()),
       
        sa.Column('project_id', sa.Integer()),
        
        sa.Column('deletion_type', sa.String(), nullable = True),
        sa.Column('change_source', sa.String(), nullable = True),

        sa.Column('archived', sa.Boolean()),
        sa.Column('is_visible', sa.Boolean(), default=True),
        sa.Column('is_public', sa.Boolean(), default=False),

        sa.Column('allowed_instance_type_list', sa.ARRAY(sa.String())),
        sa.Column('allowed_instance_template_id_list', sa.ARRAY(sa.Integer())),

        sa.Column('global_theme', JSONB),
        sa.Column('logo', JSONB),
        sa.Column('home', JSONB),
        sa.Column('undo', JSONB),
        sa.Column('redo', JSONB),
        sa.Column('complete', JSONB),
        sa.Column('defer', JSONB),
        sa.Column('zoom', JSONB),
        sa.Column('label_selector', JSONB),
        sa.Column('instance_selector', JSONB),
        sa.Column('edit_instance_template', JSONB),
        sa.Column('draw_edit', JSONB),
        sa.Column('save', JSONB),
        sa.Column('next_task', JSONB),
        sa.Column('previous_task', JSONB),
        sa.Column('guide', JSONB),
        sa.Column('brightness_contrast_filters', JSONB),
        sa.Column('hotkeys', JSONB),
        sa.Column('overflow_menu', JSONB),
        sa.Column('settings', JSONB),
        sa.Column('attributes', JSONB),
        sa.Column('instances', JSONB),
        sa.Column('userscripts', JSONB),
        sa.Column('nav_bar', JSONB),
        sa.Column('left_bar', JSONB),
        sa.Column('main_canvas', JSONB),

        sa.Column('label_settings', JSONB),

        sa.Column('allow_actions', JSONB),
        sa.Column('block_actions', JSONB),
    )
    op.create_foreign_key("member_created_id_fkey", "ui_schema", "member", ["member_created_id"], ["id"])
    op.create_foreign_key("member_updated_id_fkey", "ui_schema", "member", ["member_updated_id"], ["id"])
    op.create_foreign_key("project_id_fkey", "ui_schema", "project", ["project_id"], ["id"])


def downgrade():
    op.drop_table('ui_schema')
