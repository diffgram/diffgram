"""Add Eventhub

Revision ID: 7505d378b3ae
Revises: 7059bb6bc019
Create Date: 2021-12-09 12:19:51.495577

"""
from alembic import op
import sqlalchemy as sa
import datetime
# revision identifiers, used by Alembic.
revision = '7505d378b3ae'
down_revision = '7059bb6bc019'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('event_hub',
                    sa.Column('id', sa.BIGINT, nullable = False, primary_key = True),
                    sa.Column('kind', sa.String()),
                    sa.Column('page_name', sa.String()),
                    sa.Column('object_type', sa.String()),
                    sa.Column('description', sa.String()),
                    sa.Column('success', sa.Boolean()),
                    sa.Column('error_log', sa.String()),
                    sa.Column('run_time', sa.Float()),
                    sa.Column('link', sa.String()),
                    sa.Column('project_id', sa.Integer()),
                    sa.Column('input_id', sa.Integer()),
                    sa.Column('task_id', sa.Integer()),
                    sa.Column('task_template_id', sa.Integer()),
                    sa.Column('member_id', sa.Integer()),
                    sa.Column('file_id', sa.Integer()),
                    sa.Column('report_template_id', sa.Integer()),
                    sa.Column('report_data', sa.String()),
                    sa.Column('report_template_data', sa.String()),
                    sa.Column('time_created', sa.DateTime(), default = datetime.datetime.utcnow),

                    )
    op.add_column('event_hub', sa.Column('startup_time', sa.DateTime, default = None, nullable = True))
    op.add_column('event_hub', sa.Column('shut_down_time', sa.DateTime, default = None, nullable = True))
    op.add_column('event_hub', sa.Column('install_fingerprint', sa.String))
    op.add_column('event_hub', sa.Column('diffgram_version', sa.String))
    op.add_column('event_hub', sa.Column('previous_version', sa.String))
    op.add_column('event_hub', sa.Column('host_os', sa.String))
    op.add_column('event_hub', sa.Column('storage_backend', sa.String))
    op.add_column('event_hub', sa.Column('service_name', sa.String))
    op.add_column('event_hub', sa.Column('event_type', sa.String))

def downgrade():
    op.drop_table('event_hub')
