"""Add File Annotations Aggregate Table

Revision ID: ed8dea09f743
Revises: 73fd663f4914
Create Date: 2022-08-02 09:03:13.735264

"""
from alembic import op
import sqlalchemy as sa
import datetime

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
                    sa.Column('file_id', sa.Integer(), sa.ForeignKey('file.id')),
                    sa.Column('label_file_id', sa.Integer(), sa.ForeignKey('file.id')),

                    sa.Column('annotators_member_list', sa.ARRAY(sa.Integer), nullable = True, default = []),
                    sa.Column('attribute_value_text', sa.String(), nullable = True),
                    sa.Column('attribute_value_selected', sa.Boolean(), nullable = True),
                    sa.Column('attribute_value_selected_date', sa.DateTime(), nullable = True),
                    sa.Column('attribute_value_selected_time', sa.Time(), nullable = True),

                    sa.Column('attribute_template_id', sa.Integer(), sa.ForeignKey('attribute_template.id')),
                    sa.Column('attribute_template_group_id', sa.Integer(),
                              sa.ForeignKey('attribute_template_group.id')),
                    sa.Column('member_created_id', sa.Integer(), sa.ForeignKey('member.id')),
                    sa.Column('member_updated_id', sa.Integer(), sa.ForeignKey('member.id')),

                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_index('index__fa_label_file_id', 'file_annotations', ['label_file_id'])
    op.create_index('index__fa_label_file_id_count_instances', 'file_annotations',
                    ['label_file_id', 'count_instances'])
    op.create_index('index__fa_member_list', 'file_annotations', ['annotators_member_list'])
    op.create_index('index__fa_attributes', 'file_annotations',
                    ['attribute_template_id', 'attribute_template_group_id'])
    op.create_index('index__fa_attributes_text', 'file_annotations',
                    ['attribute_template_id', 'attribute_template_group_id', 'attribute_value_text'])
    op.create_index('index__fa_attributes_selected', 'file_annotations',
                    ['attribute_template_id', 'attribute_template_group_id', 'attribute_value_selected'])
    op.create_index('index__fa_attributes_date', 'file_annotations',
                    ['attribute_template_id', 'attribute_template_group_id', 'attribute_value_selected_date'])


def downgrade():
    op.drop_index('index__fa_label_file_id', 'file_annotations')
    op.drop_index('index__fa_label_file_id_count_instances', 'file_annotations')
    op.drop_index('index__fa_member_list', 'file_annotations')
    op.drop_index('index__fa_attributes', 'file_annotations')
    op.drop_index('index__fa_attributes_text', 'file_annotations')
    op.drop_index('index__fa_attributes_selected', 'file_annotations')
    op.drop_index('index__fa_attributes_date', 'file_annotations')
    op.drop_table('file_annotations')
