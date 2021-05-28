"""Add Model and Model Run

Revision ID: 94ac4e48a114
Revises: 990839b415fc
Create Date: 2021-05-20 10:22:15.586498

"""
from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision = '94ac4e48a114'
down_revision = '990839b415fc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('model',
                    sa.Column('id', sa.BIGINT, nullable = False, primary_key = True),
                    sa.Column('created_time', sa.DateTime(), default = datetime.datetime.utcnow),
                    sa.Column('last_updated_time', sa.DateTime(), onupdate = datetime.datetime.utcnow),
                    sa.Column('deleted_time', sa.DateTime(), nullable = True),
                    sa.Column('reference_id', sa.String()),
                    sa.Column('member_created_id', sa.Integer()),
                    sa.Column('member_updated_id', sa.Integer()),
                    sa.Column('project_id', sa.Integer()),
                    )
    op.create_foreign_key("member_created_id_fkey", "model", "member", ["member_created_id"], ["id"])
    op.create_foreign_key("member_updated_id_fkey", "model", "member", ["member_updated_id"], ["id"])
    op.create_foreign_key("project_id_fkey", "model", "project", ["project_id"], ["id"])

    op.create_table('model_run',
                    sa.Column('id', sa.BIGINT, nullable = False, primary_key = True),
                    sa.Column('created_time', sa.DateTime(), default = datetime.datetime.utcnow),
                    sa.Column('last_updated_time', sa.DateTime(), onupdate = datetime.datetime.utcnow),
                    sa.Column('deleted_time', sa.DateTime(), nullable = True),
                    sa.Column('reference_id', sa.String()),
                    sa.Column('member_created_id', sa.Integer()),
                    sa.Column('member_updated_id', sa.Integer()),
                    sa.Column('project_id', sa.Integer()),
                    sa.Column('model_id', sa.Integer()),
                    )
    op.create_foreign_key("member_created_id_fkey", "model_run", "member", ["member_created_id"], ["id"])
    op.create_foreign_key("member_updated_id_fkey", "model_run", "member", ["member_updated_id"], ["id"])
    op.create_foreign_key("project_id_fkey", "model_run", "project", ["project_id"], ["id"])
    op.create_foreign_key("model_id_fkey", "model_run", "model", ["model_id"], ["id"])

    op.add_column('instance', sa.Column('model_id', sa.Integer()))
    op.add_column('instance', sa.Column('model_run_id', sa.Integer()))
    op.create_foreign_key("model_id_fkey", "instance", "model", ["model_id"], ["id"])
    op.create_foreign_key("model_run_id_fkey", "instance", "model_run", ["model_run_id"], ["id"])
    op.create_unique_constraint('unique_model_refs', 'model', ['reference_id', 'project_id'])
    op.create_unique_constraint('unique_model_run_refs', 'model_run', ['reference_id', 'project_id', 'model_id'])

def downgrade():

    op.drop_constraint('model_id_fkey', 'instance', type_ = 'foreignkey')
    op.drop_constraint('model_run_id_fkey', 'instance', type_ = 'foreignkey')
    op.drop_constraint('unique_model_refs', 'model', type_ = 'foreignkey')
    op.drop_constraint('unique_model_run_refs', 'model_run', type_ = 'foreignkey')

    op.drop_column('instance', 'model_id')
    op.drop_column('instance', 'model_run_id')

    op.drop_constraint('member_created_id_fkey', 'model', type_ = 'foreignkey')
    op.drop_constraint('member_updated_id_fkey', 'model', type_ = 'foreignkey')
    op.drop_constraint('project_id_fkey', 'model', type_ = 'foreignkey')

    op.drop_constraint('member_created_id_fkey', 'model_run', type_ = 'foreignkey')
    op.drop_constraint('member_updated_id_fkey', 'model_run', type_ = 'foreignkey')
    op.drop_constraint('project_id_fkey', 'model_run', type_ = 'foreignkey')
    op.drop_constraint('model_id_fkey', 'model_run', type_ = 'foreignkey')

    op.drop_table('model')
    op.drop_table('model_run')
