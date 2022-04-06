"""Add Label Schema Table

Revision ID: cf7e13f71c9d
Revises: 6f3b45681519
Create Date: 2022-04-04 11:09:56.559955

"""
from alembic import op
import sqlalchemy as sa
import datetime
from sqlalchemy import orm
from shared.database.labels.label_schema import LabelSchema
from shared.database.user import User
from shared.database.auth.member import Member
from shared.database.project import Project, UserbaseProject
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from shared.database.source_control.working_dir import WorkingDir, WorkingDirFileLink
from shared.database.source_control.file import File
from sqlalchemy.ext.declarative import declarative_base

# revision identifiers, used by Alembic.
revision = 'cf7e13f71c9d'
down_revision = '6f3b45681519'
branch_labels = None
depends_on = None

Base = declarative_base()


def add_schemas_to_projects(op):
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    all_projects = session.query(Project).all()
    if len(all_projects) == 0:
        return
    super_admin = session.query(User).filter(
        User.is_super_admin == True
    ).first()
    if not super_admin:
        raise Exception('Cannot migrated data, need at least one super admin user. Please set a user with super_admin flag enabled')
    member = session.query(Member).filter(
        Member.user_id == super_admin.id
    ).first()
    print('Creating Schemas for all projects')
    i = 0
    for project in all_projects:

        new_schema = LabelSchema.new(
            session = session,
            name = 'Default Schema',
            project_id = project.id,
            member_created_id = member.id
        )
        directory = project.directory_default
        if directory is None:
            label_file_list = session.query(File).filter(
                File.project_id == project.id, File.type == 'label').all()
        else:
            working_dir_sub_query = session.query(WorkingDirFileLink).filter(
                WorkingDirFileLink.working_dir_id == directory.id,
                WorkingDirFileLink.type == "label").subquery('working_dir_sub_query')

            label_file_list = session.query(File).filter(
                File.id == working_dir_sub_query.c.file_id).all()

        for label_file in label_file_list:
            rel = new_schema.add_label_file(session, label_file.id, member.id)
            print(f'      --> Added Label: {label_file.label.name} to Schema')

        attribute_groups_archived = Attribute_Template_Group.list(
            session = session,
            project_id = project.id,
            archived = True,
            limit = None
        )
        attribute_groups = Attribute_Template_Group.list(
            session = session,
            project_id = project.id,
            archived = False,
            limit = None
        )
        attribute_groups_list = attribute_groups + attribute_groups_archived
        print(f'Num Projects [{i}/{len(all_projects) - 1}]')
        i += 1



def upgrade():
    op.create_table('label_schema',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('name', sa.String(), nullable = False),
                    sa.Column('project_id', sa.Integer(), sa.ForeignKey('project.id')),
                    sa.Column('archived', sa.Boolean(), default = False),
                    sa.Column('member_created_id', sa.Integer(), sa.ForeignKey('member.id')),
                    sa.Column('member_updated_id', sa.Integer(), sa.ForeignKey('member.id')),
                    sa.Column('time_created', sa.DateTime, default = datetime.datetime.utcnow),
                    sa.Column('time_updated', sa.DateTime, onupdate = datetime.datetime.utcnow),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('index_label_schema_project_id', 'label_schema', ['project_id'])

    op.create_table('label_schema_link',
                    sa.Column('id', sa.Integer(), nullable = False),
                    sa.Column('schema_id', sa.Integer(), sa.ForeignKey('label_schema.id')),
                    sa.Column('label_file_id', sa.Integer(), sa.ForeignKey('file.id')),
                    sa.Column('instance_template_id', sa.Integer(), sa.ForeignKey('instance_template.id')),
                    sa.Column('attribute_template_group_id', sa.Integer(), sa.ForeignKey('attribute_template_group.id')),
                    sa.Column('member_created_id', sa.Integer(), sa.ForeignKey('member.id')),
                    sa.Column('member_updated_id', sa.Integer(), sa.ForeignKey('member.id')),
                    sa.Column('time_created', sa.DateTime, default = datetime.datetime.utcnow),
                    sa.Column('time_updated', sa.DateTime, onupdate = datetime.datetime.utcnow),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('index_label_schema_link_schema_id', 'label_schema_link', ['schema_id'])
    op.create_index('index_label_schema_link_label_file_id', 'label_schema_link', ['label_file_id'])
    
    op.create_index('index_attribute_template_project_id', 'attribute_template', ['project_id'])

    add_schemas_to_projects(op)

def downgrade():
    op.drop_index('index_label_schema_project_id', 'label_schema')
    op.drop_index('index_label_schema_link_schema_id', 'label_schema_link')
    op.drop_index('index_label_schema_link_label_file_id', 'label_schema_link')
    op.drop_index('index_attribute_template_project_id', 'attribute_template')

    op.drop_table('label_schema_link')
    op.drop_table('label_schema')

