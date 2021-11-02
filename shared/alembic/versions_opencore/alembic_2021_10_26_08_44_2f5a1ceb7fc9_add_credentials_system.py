"""Add Credentials System

Revision ID: 2f5a1ceb7fc9
Revises: bdcd484ece5f
Create Date: 2021-10-26 08:44:24.153134

"""
from alembic import op
import sqlalchemy as sa
from shared.database.core import MutableDict, JSONEncodedDict
# revision identifiers, used by Alembic.
revision = '2f5a1ceb7fc9'
down_revision = 'bdcd484ece5f'
branch_labels = None
depends_on = None


def upgrade():

    op.create_table('credential_type',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('name', sa.String(), nullable = True),
                    sa.Column('description_markdown', sa.String(), nullable = True),
                    sa.Column('project_id', sa.Integer(), nullable = True),
                    sa.Column('archived', sa.Boolean(), nullable = True),
                    sa.Column('history_cache', JSONEncodedDict(), nullable = True),
                    sa.Column('public', sa.Boolean(), nullable = True),
                    sa.Column('image_id', sa.Integer(), nullable = True),
                    sa.Column('member_created_id', sa.Integer(), nullable = True),
                    sa.Column('member_updated_id', sa.Integer(), nullable = True),
                    sa.Column('time_created', sa.DateTime(), nullable = True),
                    sa.Column('time_updated', sa.DateTime(), nullable = True),
                    sa.ForeignKeyConstraint(['image_id'], ['image.id'], ),
                    sa.ForeignKeyConstraint(['member_created_id'], ['member.id'], ),
                    sa.ForeignKeyConstraint(['member_updated_id'], ['member.id'], ),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('credential',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('credential_type_id', sa.Integer(), nullable = True),
                    sa.Column('user_id', sa.Integer(), nullable = True),
                    sa.Column('status', sa.String(), nullable = True),
                    sa.Column('external_id', sa.String(), nullable = True),
                    sa.Column('image_id', sa.Integer(), nullable = True),
                    sa.Column('time_created', sa.DateTime(), nullable = True),
                    sa.Column('time_updated', sa.DateTime(), nullable = True),
                    sa.ForeignKeyConstraint(['credential_type_id'], ['credential_type.id'], ),
                    sa.ForeignKeyConstraint(['image_id'], ['image.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['userbase.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('credential_type_to_job',
                    sa.Column('credential_type_id', sa.Integer(), nullable = False),
                    sa.Column('job_id', sa.Integer(), nullable = False),
                    sa.Column('kind', sa.String(), nullable = True),
                    sa.ForeignKeyConstraint(['credential_type_id'], ['credential_type.id'], ),
                    sa.ForeignKeyConstraint(['job_id'], ['job.id'], ),
                    sa.PrimaryKeyConstraint('credential_type_id', 'job_id')
                    )


def downgrade():

    op.drop_table('credential_type_to_job')
    op.drop_table('credential')
    op.drop_table('credential_type')

