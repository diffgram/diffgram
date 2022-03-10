from shared.database.common import *
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import desc
from sqlalchemy import nullslast

from shared.shared_logger import get_shared_logger
logger = get_shared_logger()
from sqlalchemy.dialects.postgresql import JSONB


class UI_Schema(Base, SerializerMixin):
    """
    

    """
    __tablename__ = 'ui_schema'

    id = Column(BIGINT, primary_key = True)

    name = Column(String)
    note = Column(String)

    version = Column(Integer, default = 0)

    created_time = Column(DateTime, default = datetime.datetime.utcnow)
    last_updated_time = Column(DateTime, onupdate = datetime.datetime.utcnow)

    client_created_time = Column(DateTime, nullable = True)
    creation_ref_id = Column(String(), nullable = True)

    deleted_time = Column(DateTime, nullable = True)

    archived = Column(Boolean)
    is_visible = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)

    deletion_type = Column(String, nullable = True)
    change_source = Column(String, nullable = True)

    project_id = Column(Integer, ForeignKey('project.id'), index=True)
    project = relationship("Project")

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    allowed_instance_type_list = Column(ARRAY(String()))
    allowed_instance_template_id_list = Column(ARRAY(Integer()))

    # {visible: bool,
    #  url: example,
    #  style: example}

    global_theme = Column(MutableDict.as_mutable(JSONB))

    logo = Column(MutableDict.as_mutable(JSONB))
    home = Column(MutableDict.as_mutable(JSONB))
    task_list = Column(MutableDict.as_mutable(JSONB))
    undo = Column(MutableDict.as_mutable(JSONB))
    redo = Column(MutableDict.as_mutable(JSONB))
    complete = Column(MutableDict.as_mutable(JSONB))
    defer = Column(MutableDict.as_mutable(JSONB))
    zoom = Column(MutableDict.as_mutable(JSONB))
    label_selector = Column(MutableDict.as_mutable(JSONB))
    instance_selector = Column(MutableDict.as_mutable(JSONB))
    edit_instance_template = Column(MutableDict.as_mutable(JSONB))
    draw_edit = Column(MutableDict.as_mutable(JSONB))
    save = Column(MutableDict.as_mutable(JSONB))
    next_task = Column(MutableDict.as_mutable(JSONB))
    previous_task = Column(MutableDict.as_mutable(JSONB))
    guide = Column(MutableDict.as_mutable(JSONB))
    brightness_contrast_filters = Column(MutableDict.as_mutable(JSONB))
    hotkeys = Column(MutableDict.as_mutable(JSONB))
    overflow_menu = Column(MutableDict.as_mutable(JSONB))
    settings = Column(MutableDict.as_mutable(JSONB))

    attributes = Column(MutableDict.as_mutable(JSONB))
    instances = Column(MutableDict.as_mutable(JSONB))
    userscripts = Column(MutableDict.as_mutable(JSONB))
    nav_bar = Column(MutableDict.as_mutable(JSONB))
    left_bar = Column(MutableDict.as_mutable(JSONB))

    main_canvas = Column(MutableDict.as_mutable(JSONB))

    label_settings = Column(MutableDict.as_mutable(JSONB))

    allow_actions = Column(MutableDict.as_mutable(JSONB))
    block_actions = Column(MutableDict.as_mutable(JSONB))
    time_tracking = Column(MutableDict.as_mutable(JSONB))
    # example actions

    #allow_instance_delete 
    #allow_instance_move 
    #allow_new_instance_creation 
    #allow_new_instance_creation 
    #allow_label_change 
    #allow_attribute_change 
    #allow_copy_paste 
    #allow_new_template_creation 
    #allow_history_access 

    #allow_edit_of_complete_task = Column(Boolean)

    # These should be rolled into label settings maybe?
    #default_to_view_only_mode
    #default_to_qa_slideshow


    def serialize(self):
        # https://github.com/n0nSmoker/SQLAlchemy-serializer
        return self.to_dict(rules=(
            '-member_created', 
            '-member_updated',
            '-project'))


    @staticmethod
    def get_by_id(session,
                  id: int):

        return session.query(UI_Schema).filter(
            UI_Schema.id == id).first()


    @staticmethod
    def get(session,
            id: int,
            project_id: int):

        query = session.query(UI_Schema)
        query = query.filter(UI_Schema.id == id)
        query = query.filter(or_(
            UI_Schema.project_id == project_id,
            UI_Schema.is_public == True
            ))

        return query.first()



    @staticmethod
    def list(
            session,
            project_id=None,
            org=None,
            limit=100,
            return_kind="objects",
            archived = False,
            date_to = None,     # datetime
            date_from = None,   # datetime
            date_to_string: str = None,
            date_from_string: str = None,
            name: str = None,
            name_match_type: str = "ilike",  # substring and helps if case Aa is off
            order_by_class_and_attribute = None,
            order_by_direction = desc,
            public_only = False
            ):
        """


        """
        query = session.query(UI_Schema)

        # Assume we must either have public  or project id
        if public_only is True:
            query = query.filter(UI_Schema.is_public == True)
        else:
            query = query.filter(UI_Schema.project_id == project_id)

        if name:
            if name_match_type == "ilike":
                name_search = f"%{name}%"
                query = query.filter(UI_Schema.name.ilike(name_search))
            else:
                query = query.filter(UI_Schema.name == name)

        if date_from or date_to:
            if date_from:
                query = query.filter(UI_Schema.created_time >= date_from)
            if date_to:
                query = query.filter(UI_Schema.created_time <= date_to)

        elif date_from_string or date_to_string:
            query = regular_methods.regular_query(
                query=query,
                date_from_string=date_from_string,
                date_to_string=date_to_string,
                base_class=UI_Schema,
                created_time_string='last_updated_time'
            )

        if archived is False:   
            query = query.filter(or_(
                UI_Schema.archived == None,
                UI_Schema.archived == False))

        if order_by_class_and_attribute:
           query = query.order_by(
              nullslast(order_by_direction(order_by_class_and_attribute)))

        if return_kind == "count":
            return query.limit(limit).count()

        if return_kind == "objects":
            return query.limit(limit).all()


    @staticmethod
    def new(
            member_created: 'Member' = None,
            project: 'Project' = None,
            client_created_time = None,
            creation_ref_id = None,
            name = None
            ) -> 'UI_Schema':

        return UI_Schema(**locals())   
