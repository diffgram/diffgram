"""Add Relations to Instance

Revision ID: e3f6f51e6bd5
Revises: e18fd230021b
Create Date: 2022-01-24 12:35:43.702355

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3f6f51e6bd5'
down_revision = '8736666d667d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('instance', sa.Column('from_instance_id',
                                        sa.Integer,
                                        nullable = True,
                                        default = None))
    op.add_column('instance', sa.Column('to_instance_id',
                                        sa.Integer,
                                        nullable = True,
                                        default = None))

    op.execute('ALTER TABLE instance ADD CONSTRAINT instance_from_instance_id_fkey FOREIGN KEY (from_instance_id) REFERENCES instance (id) NOT VALID;')
    op.execute('ALTER TABLE instance ADD CONSTRAINT instance_to_instance_id_fkey FOREIGN KEY (to_instance_id) REFERENCES instance (id) NOT VALID;')


def downgrade():
    op.drop_column('instance', 'from_instance_id')
    op.drop_column('instance', 'to_instance_id')
