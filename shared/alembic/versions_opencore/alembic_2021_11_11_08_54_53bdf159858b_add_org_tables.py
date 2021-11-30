"""Add Organization Tables

Revision ID: 53bdf159858b
Revises: 3c761954bd8d
Create Date: 2021-11-11 08:54:04.701754

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '53bdf159858b'
down_revision = '3c761954bd8d'
branch_labels = None
depends_on = None


def upgrade():
    org = op.create_table('org',
                          sa.Column('id', sa.Integer(), nullable = False),
                          sa.Column('security_disable', sa.Boolean(), nullable = True),
                          sa.Column('verified_by_diffgram', sa.Boolean(), nullable = True),
                          sa.Column('name', sa.String(), nullable = True),
                          sa.Column('api_address_valid', sa.Boolean(), nullable = True),
                          sa.Column('api_trainer_org', sa.Boolean(), nullable = True),
                          sa.Column('address_primary_id', sa.Integer(), nullable = True),
                          sa.Column('primary_user_id', sa.Integer(), nullable = True),
                          sa.Column('member_created_id', sa.Integer(), nullable = True),
                          sa.Column('member_updated_id', sa.Integer(), nullable = True),
                          sa.Column('time_created', sa.DateTime(), nullable = True),
                          sa.Column('time_updated', sa.DateTime(), nullable = True),
                          sa.Column('remote_address_created', sa.String(), nullable = True),
                          sa.PrimaryKeyConstraint('id')
                          )
    # Org constraints
    # sa.ForeignKeyConstraint(['address_primary_id'], ['address.id'], table=org)
    op.create_foreign_key("org_address_primary_id_fkey", "org", "address", ["address_primary_id"], ["id"])
    # sa.ForeignKeyConstraint(['member_created_id'], ['member.id'], table=org)
    op.create_foreign_key("org_member_created_id_fkey", "org", "member", ["member_created_id"], ["id"])
    # sa.ForeignKeyConstraint(['member_updated_id'], ['member.id'], table=org)
    op.create_foreign_key("org_member_updated_id_fkey", "org", "member", ["member_updated_id"], ["id"])
    # sa.ForeignKeyConstraint(['primary_user_id'], ['userbase.id'], table=org)
    op.create_foreign_key("org_primary_user_id_fkey", "org", "userbase", ["primary_user_id"], ["id"])

    op.create_table('org_to_user',
                    sa.Column('org_id', sa.Integer(), nullable = False),
                    sa.Column('user_id', sa.Integer(), nullable = False),
                    sa.Column('user_permission_level', sa.String(), nullable = True),
                    sa.Column('time_created', sa.DateTime(), nullable = True),
                    sa.Column('time_updated', sa.DateTime(), nullable = True),
                    sa.ForeignKeyConstraint(['org_id'], ['org.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['userbase.id'], ),
                    sa.PrimaryKeyConstraint('org_id', 'user_id')
                    )

    op.add_column('project', sa.Column('org_id', sa.Integer, sa.ForeignKey('org.id')))


def downgrade():
    op.drop_column('project', 'org_id')
    op.drop_table('org_to_user')
    op.drop_table('org')
