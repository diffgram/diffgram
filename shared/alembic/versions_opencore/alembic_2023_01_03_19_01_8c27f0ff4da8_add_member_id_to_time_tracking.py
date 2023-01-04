"""add member id to time tracking

Revision ID: 8c27f0ff4da8
Revises: a576f5a04c03
Create Date: 2023-01-03 19:01:05.825976

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm

# revision identifiers, used by Alembic.
revision = '8c27f0ff4da8'
down_revision = 'a576f5a04c03'
branch_labels = None
depends_on = None


def migrate_existing_time_tracking():
    from shared.database.task.task_time_tracking import TaskTimeTracking
    from shared.database.auth.member import Member

    bind = op.get_bind()
    session = orm.Session(bind = bind)
    task_time_track_list = session.query(TaskTimeTracking).all()
    for task_time_track in task_time_track_list:
        member = Member.get_by_user_id(
            session = session, 
            user_id = task_time_track.user_id)
        task_time_track.member_id = member.id
        print(f'Migrating: {task_time_track.id} UserID: {task_time_track.user_id}  MemberID: {task_time_track.member_id}')
        session.add(task_time_track)


def upgrade():
    op.add_column('task_time_tracking', sa.Column('member_id', sa.Integer()))
    migrate_existing_time_tracking()

def downgrade():
    op.drop_column('task_time_tracking', 'member_id')