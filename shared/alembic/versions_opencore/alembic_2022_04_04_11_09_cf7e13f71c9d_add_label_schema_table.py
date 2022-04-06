"""Add Label Schema Table

Revision ID: cf7e13f71c9d
Revises: 6f3b45681519
Create Date: 2022-04-04 11:09:56.559955

"""
from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision = 'cf7e13f71c9d'
down_revision = '6f3b45681519'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('label_schema',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('name', sa.String(), nullable = False),
                    sa.Column('project_id', sa.Integer(), sa.ForeignKey('project.id')),
                    sa.Column('archived', sa.Boolean(), default = False),
                    sa.Column('member_created_id', sa.Integer(), sa.ForeignKey('member.id')),
                    sa.Column('member_updated_id', sa.Integer(), sa.ForeignKey('member.id')),
                    sa.Column('time_created', sa.DateTime, default = datetime.datetime.utcnow),
                    sa.Column('time_updated', sa.DateTime, onupdate = datetime.datetime.utcnow),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('index_label_schema_project_id', 'label_schema', ['project_id'])

    op.create_table('label_schema_link',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('schema_id', sa.Integer(), sa.ForeignKey('label_schema.id')),
                    sa.Column('label_file_id', sa.Integer(), sa.ForeignKey('file.id')),
                    sa.Column('member_created_id', sa.Integer(), sa.ForeignKey('member.id')),
                    sa.Column('member_updated_id', sa.Integer(), sa.ForeignKey('member.id')),
                    sa.Column('time_created', sa.DateTime, default = datetime.datetime.utcnow),
                    sa.Column('time_updated', sa.DateTime, onupdate = datetime.datetime.utcnow),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('index_label_schema_link_schema_id', 'label_schema_link', ['schema_id'])
    op.create_index('index_label_schema_link_label_file_id', 'label_schema_link', ['label_file_id'])
    
    op.create_index('index_attribute_template_project_id', 'attribute_template', ['project_id'])


def downgrade():
    op.drop_index('index_label_schema_project_id', 'label_schema')
    op.drop_index('index_label_schema_link_schema_id', 'label_schema_link')
    op.drop_index('index_label_schema_link_label_file_id', 'label_schema_link')
    op.drop_index('index_attribute_template_project_id', 'attribute_template')

    op.drop_table('label_schema')
    op.drop_table('label_schema_link')
