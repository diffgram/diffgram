"""Add system configs table

Revision ID: 9cfc913ef62d
Revises: 7c18149a20c8
Create Date: 2023-04-24 09:54:30.114043

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9cfc913ef62d'
down_revision = '3dda228d38f0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('system_configs',
                    sa.Column('id', sa.BIGINT, nullable = False, primary_key = True),
                    sa.Column('image_id', sa.Integer())
                    )


    op.create_foreign_key("image_id_fkey", "system_configs", "image", ["image_id"], ["id"])


def downgrade():
    op.drop_table('system_configs')

