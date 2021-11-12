"""Add Account Tables

Revision ID: dc4baf8d8f61
Revises: 3c50e7d2bb18
Create Date: 2021-11-12 09:18:06.568109

"""
from alembic import op
import sqlalchemy as sa
from shared.database.core import JSONEncodedDict
# revision identifiers, used by Alembic.
revision = 'dc4baf8d8f61'
down_revision = '3c50e7d2bb18'
branch_labels = None
depends_on = None


def upgrade():
    account = op.create_table('account',
                              sa.Column('id', sa.Integer(), nullable = False),
                              sa.Column('nickname', sa.String(), nullable = True),
                              sa.Column('mode_trainer_or_builder', sa.String(), nullable = True),
                              sa.Column('account_type', sa.String(), nullable = True),
                              sa.Column('credit_limit', sa.Integer(), nullable = True),
                              sa.Column('payment_method_on_file', sa.Boolean(), nullable = True),
                              sa.Column('security_disable', sa.Boolean(), nullable = True),
                              sa.Column('transaction_previous_id', sa.Integer(), nullable = True),
                              sa.Column('address_primary_id', sa.Integer(), nullable = True),
                              sa.Column('primary_user_id', sa.Integer(), nullable = True),
                              sa.Column('stripe_id', sa.String(), nullable = True),
                              sa.Column('member_created_id', sa.Integer(), nullable = True),
                              sa.Column('member_updated_id', sa.Integer(), nullable = True),
                              sa.Column('time_created', sa.DateTime(), nullable = True),
                              sa.Column('time_updated', sa.DateTime(), nullable = True),
                              sa.PrimaryKeyConstraint('id')
                              )
    # account constraints
    # sa.ForeignKeyConstraint(['address_primary_id'], ['address.id'], table=account)
    op.create_foreign_key("account_address_primary_id_fkey", "account", "address", ["address_primary_id"], ["id"])
    # sa.ForeignKeyConstraint(['member_created_id'], ['member.id'], table=account)
    op.create_foreign_key("account_member_created_id_fkey", "account", "member", ["member_created_id"], ["id"])
    # sa.ForeignKeyConstraint(['member_updated_id'], ['member.id'], table=account)
    op.create_foreign_key("account_member_updated_id_fkey", "account", "member", ["member_updated_id"], ["id"])
    # sa.ForeignKeyConstraint(['primary_user_id'], ['userbase.id'], table=account)
    op.create_foreign_key("account_primary_user_id_fkey", "account", "userbase", ["primary_user_id"], ["id"])

    op.create_table('plan_template',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('public_name', sa.String(), nullable = True),
                    sa.Column('internal_name', sa.String(), nullable = True),
                    sa.Column('kind', sa.String(), nullable = True),
                    sa.Column('limit_instances', sa.Integer(), nullable = True),
                    sa.Column('limit_projects', sa.Integer(), nullable = True),
                    sa.Column('limit_files', sa.Integer(), nullable = True),
                    sa.Column('limit_users_per_project', sa.Integer(), nullable = True),
                    sa.Column('limit_video_frames_per_file', sa.Integer(), nullable = True),
                    sa.Column('included_monthly_training_credits', sa.Integer(), nullable = True),
                    sa.Column('cost_monthly', sa.Integer(), nullable = True),
                    sa.Column('may_buy_instances', sa.Boolean(), nullable = True),
                    sa.Column('cost_per_1000_instances', sa.Integer(), nullable = True),
                    sa.Column('cost_per_training_hour', sa.Integer(), nullable = True),
                    sa.Column('cost_annual', sa.Integer(), nullable = True),
                    sa.Column('feature_sla', sa.String(), nullable = True),
                    sa.Column('feature_support', sa.String(), nullable = True),
                    sa.Column('feature_user_management', sa.String(), nullable = True),
                    sa.Column('is_available', sa.Boolean(), nullable = True),
                    sa.Column('is_public', sa.Boolean(), nullable = True),
                    sa.Column('is_free', sa.Boolean(), nullable = True),
                    sa.Column('export_models_allowed', sa.Boolean(), nullable = True),
                    sa.Column('time_created', sa.DateTime(), nullable = True),
                    sa.Column('time_updated', sa.DateTime(), nullable = True),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('plan',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('template_id', sa.Integer(), nullable = True),
                    sa.Column('is_active', sa.Boolean(), nullable = True),
                    sa.Column('member_created_id', sa.Integer(), nullable = True),
                    sa.Column('member_updated_id', sa.Integer(), nullable = True),
                    sa.Column('time_created', sa.DateTime(), nullable = True),
                    sa.Column('time_ended', sa.DateTime(), nullable = True),
                    sa.Column('time_updated', sa.DateTime(), nullable = True),
                    sa.ForeignKeyConstraint(['member_created_id'], ['member.id'], ),
                    sa.ForeignKeyConstraint(['member_updated_id'], ['member.id'], ),
                    sa.ForeignKeyConstraint(['template_id'], ['plan_template.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.add_column('userbase', sa.Column('default_plan_id', sa.Integer(), nullable = True))
    op.add_column('project', sa.Column('plan_id', sa.Integer(), nullable = True))
    op.create_foreign_key("project_plan_id_fkey", "project", "plan", ["plan_id"], ["id"])
    op.create_foreign_key("userbase_default_plan_id_fkey", "userbase", "plan", ["default_plan_id"], ["id"])

    op.create_table('transaction',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('account_id', sa.Integer(), nullable=True),
                    sa.Column('transaction_previous_id', sa.Integer(), nullable=True),
                    sa.Column('transaction_related_id', sa.Integer(), nullable=True),
                    sa.Column('transaction_type', sa.String(), nullable=True),
                    sa.Column('sub_kind', sa.String(), nullable=True),
                    sa.Column('amount', sa.Integer(), nullable=True),
                    sa.Column('balance_new', sa.Integer(), nullable=True),
                    sa.Column('cost_per_instance', sa.Integer(), nullable=True),
                    sa.Column('count_instances_changed', sa.Integer(), nullable=True),
                    sa.Column('task_id', sa.Integer(), nullable=True),
                    sa.Column('job_id', sa.Integer(), nullable=True),
                    sa.Column('project_id', sa.Integer(), nullable=True),
                    sa.Column('time_created', sa.DateTime(), nullable=True),
                    sa.Column('time_updated', sa.DateTime(), nullable=True),
                    sa.Column('audit_cache', JSONEncodedDict(), nullable=True),
                    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
                    sa.ForeignKeyConstraint(['job_id'], ['job.id'], ),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
                    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
                    sa.ForeignKeyConstraint(['transaction_previous_id'], ['transaction.id'], ),
                    sa.ForeignKeyConstraint(['transaction_related_id'], ['transaction.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_foreign_key("account_transaction_previous_id_fkey", "account", "transaction", ["transaction_previous_id"], ["id"])


def downgrade():
    op.drop_constraint('account_transaction_previous_id_fkey', 'account')
    op.drop_constraint('userbase_default_plan_id_fkey', 'userbase')
    op.drop_constraint('project_plan_id_fkey', 'project')
    op.drop_constraint('account_primary_user_id_fkey', 'account')
    op.drop_constraint('account_member_updated_id_fkey', 'account')
    op.drop_constraint('account_member_created_id_fkey', 'account')
    op.drop_constraint('account_address_primary_id_fkey', 'account')
    op.drop_column('userbase', 'default_plan_id')
    op.drop_column('project', 'plan_id')
    op.drop_table('transaction')
    op.drop_table('plan')
    op.drop_table('plan_template')
    op.drop_table('account')
