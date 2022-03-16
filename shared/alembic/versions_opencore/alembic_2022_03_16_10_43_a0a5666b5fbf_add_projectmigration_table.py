"""Add ProjectMigration table

Revision ID: a0a5666b5fbf
Revises: 13dc81c0b35d
Create Date: 2022-03-16 10:43:00.630024

"""
from alembic import op
import sqlalchemy as sa
import datetime
from shared.database.core import MutableDict, JSONEncodedDict
from sqlalchemy.dialects.postgresql import JSONB
from shared.regular import regular_log

# revision identifiers, used by Alembic.
revision = 'a0a5666b5fbf'
down_revision = '13dc81c0b35d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('project_migration',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('created_time', sa.DateTime, default = datetime.datetime.utcnow),
                    sa.Column('time_completed', sa.DateTime),
                    sa.Column('time_updated', sa.DateTime, onupdate = datetime.datetime.utcnow),
                    sa.Column('time_last_attempted', sa.DateTime),
                    sa.Column('type', sa.String()),
                    sa.Column('status', sa.String(), default = 'in_progress'),
                    sa.Column('percent_complete', sa.Float(), default = 0.0),
                    sa.Column('description', sa.String()),
                    sa.Column('external_mapping_project_id', sa.Integer, sa.ForeignKey('external_map.id')),
                    sa.Column('connection_id', sa.Integer, sa.ForeignKey('connection_base.id')),
                    sa.Column('error_log', MutableDict.as_mutable(JSONB)),
                    sa.Column('retry_count', sa.Integer, default = 0),
                    sa.Column('import_schema', sa.Boolean, default = True),
                    sa.Column('import_files', sa.Boolean, default = False),
                    sa.Column('project_id', sa.Integer, sa.ForeignKey('project.id')),
                    sa.Column('migration_log', MutableDict.as_mutable(JSONB), default = regular_log.default()),
                    sa.Column('member_created_id', sa.Integer(), sa.ForeignKey('member.id')),
                    sa.Column('member_updated_id', sa.Integer(), sa.ForeignKey('member.id')),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('project_migration')
