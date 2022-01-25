"""Add Tokenizer Columns

Revision ID: e18fd230021b
Revises: e25f886d921a
Create Date: 2022-01-20 10:22:22.407632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e18fd230021b'
down_revision = 'e25f886d921a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('instance', sa.Column('text_tokenizer', sa.String, default = 'nltk'))
    op.add_column('file', sa.Column('text_tokenizer', sa.String, default = 'nltk'))
    op.add_column('task', sa.Column('text_tokenizer', sa.String, default = 'nltk'))


def downgrade():
    op.drop_column('instance', 'text_tokenizer')
    op.drop_column('file', 'text_tokenizer')
    op.drop_column('task', 'text_tokenizer')
