"""Add exams table

Revision ID: 7f30723acfcd
Revises: e18fd230021b
Create Date: 2022-01-28 10:17:31.387713

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7f30723acfcd'
down_revision = 'e1739d7f895f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('exam',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('credentials_awarded', sa.Boolean()),
                    sa.Column('user_taking_exam_id', sa.Integer(), sa.ForeignKey('userbase.id')),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.add_column('job', sa.Column('exam_id', sa.Integer(), sa.ForeignKey('exam.id')))


def downgrade():
    op.drop_table('exam')
    op.drop_column('job', 'exam_id')
