"""Add Instance Relation Table

Revision ID: eee80271ae05
Revises: e25f886d921a
Create Date: 2022-01-17 10:03:41.912796

"""
from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision = 'eee80271ae05'
down_revision = 'e25f886d921a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('instance_relation',
                    sa.Column('id', sa.BIGINT, nullable = False, primary_key = True),
                    sa.Column('type', sa.String()),
                    sa.Column('from_instance_id', sa.Integer(),  sa.ForeignKey('instance.id')),
                    sa.Column('to_instance_id', sa.Integer(), sa.ForeignKey('instance.id')),
                    sa.Column('member_created_id', sa.Integer()),
                    sa.Column('member_updated_id', sa.Boolean()),
                    sa.Column('time_created', sa.DateTime(), default = datetime.datetime.utcnow),
                    sa.Column('time_updated', sa.DateTime(), onupdate = datetime.datetime.utcnow),

                    )

    op.add_column('instance', sa.Column('instance_relations_cache', sa.dialects.postgresql.JSONB, default = []))


def downgrade():
    op.drop_column('instance', 'instance_relations_cache')
    op.drop_table('instance_relation')
