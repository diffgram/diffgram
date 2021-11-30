"""Add Default Action Templates

Revision ID: 7059bb6bc019
Revises: dc4baf8d8f61
Create Date: 2021-11-12 10:08:21.445826

"""
from alembic import op
import sqlalchemy as sa
from shared.database_setup_supporting import *
from shared.helpers.sessionMaker import session_scope
from shared.database.action.action_template import Action_Template
from sqlalchemy import orm

# revision identifiers, used by Alembic.
revision = '7059bb6bc019'
down_revision = 'dc4baf8d8f61'
branch_labels = None
depends_on = None


def add_action_templates(session):
    Action_Template.new(
        session = session,
        public_name = 'count',
        kind = 'count',
        category = None
    )
    Action_Template.new(
        session = session,
        public_name = 'condition',
        kind = 'condition',
        category = None
    )
    Action_Template.new(
        session = session,
        public_name = 'delay',
        kind = 'delay',
        category = None
    )
    Action_Template.new(
        session = session,
        public_name = 'email',
        kind = 'email',
        category = None
    )
    Action_Template.new(
        session = session,
        public_name = 'webhook',
        kind = 'webhook',
        category = None
    )
    session.commit()

def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    add_action_templates(session)


def downgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    result = session.query(Action_Template).filter(
        Action_Template.kind.in_([
            'count',
            'delay',
            'condition',
            'email',
            'webhook'
        ])
    ).all()

    for temp in result:
        session.delete(temp)
