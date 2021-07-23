"""Add System Events

Revision ID: ee39eac32ff8
Revises: 7ff038954a96
Create Date: 2021-07-23 10:58:04.819668

"""
from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision = 'ee39eac32ff8'
down_revision = '7ff038954a96'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('system_events',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('kind', sa.String()),
                    sa.Column('description', sa.String()),
                    sa.Column('install_fingerprint', sa.String()),
                    sa.Column('previous_version', sa.String()),
                    sa.Column('diffgram_version', sa.String()),
                    sa.Column('host_os', sa.String()),
                    sa.Column('storage_backend', sa.String()),
                    sa.Column('service_name', sa.String()),
                    sa.Column('startup_time', sa.DateTime, default = None, nullable = True),
                    sa.Column('shut_down_time', sa.DateTime, default = None, nullable = True),
                    sa.Column('created_date', sa.DateTime, default = datetime.datetime.utcnow),
                    )

    op.add_column('event', sa.Column('install_fingerprint', sa.String))
    op.add_column('event', sa.Column('diffgram_version', sa.String))


def downgrade():
    op.drop_column('event', 'install_fingerprint')
    op.drop_column('event', 'diffgram_version')

    op.drop_table('system_events')
