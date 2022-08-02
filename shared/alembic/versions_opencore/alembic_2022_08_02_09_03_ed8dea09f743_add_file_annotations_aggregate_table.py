"""Add File Annotations Aggregate Table

Revision ID: ed8dea09f743
Revises: 73fd663f4914
Create Date: 2022-08-02 09:03:13.735264

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ed8dea09f743'
down_revision = '73fd663f4914'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('file_annotations',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('created_time', sa.DateTime, default = datetime.datetime.utcnow),
                    sa.Column('count_instances', sa.Integer()),
                    sa.Column('label_file_id', sa.Integer(), sa.ForeignKey('file.id')),

                    sa.Column('annotators_member_list', sa.ARRAY(sa.Integer), nullable = True, default = []),
                    sa.Column('attribute_value_selected', sa.String(), sa.ForeignKey('file.id')),

                    sa.Column('host_os', sa.String()),
                    sa.Column('storage_backend', sa.String()),
                    sa.Column('service_name', sa.String()),
                    sa.Column('startup_time', sa.DateTime, default = None, nullable = True),
                    sa.Column('shut_down_time', sa.DateTime, default = None, nullable = True),

                    sa.PrimaryKeyConstraint('id')
                    )

    op.add_column('event', sa.Column('install_fingerprint', sa.String))
    op.add_column('event', sa.Column('diffgram_version', sa.String))


def downgrade():
    op.drop_column('event', 'install_fingerprint')
    op.drop_column('event', 'diffgram_version')

    op.drop_table('system_events')
