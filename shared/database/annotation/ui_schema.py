from shared.database.common import *
from sqlalchemy_serializer import SerializerMixin

from shared.shared_logger import get_shared_logger
logger = get_shared_logger()


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

    is_template = Column(Boolean, default = False)

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])


    show_logo = Column(Boolean)
    show_home_button = Column(Boolean)
    show_undo = Column(Boolean)
    show_redo = Column(Boolean)
    show_complete = Column(Boolean)
    show_defer = Column(Boolean)
    show_zoom = Column(Boolean)
    show_labels = Column(Boolean)
    show_instance_selector = Column(Boolean)
    show_draw_edit = Column(Boolean)
    show_save = Column(Boolean)
    show_next_task = Column(Boolean)
    show_previous_task = Column(Boolean)
    show_guide = Column(Boolean)
    show_brightness_contrast_filters = Column(Boolean)
    show_hotkeys = Column(Boolean)
    show_overflow_menu = Column(Boolean)
    show_settings = Column(Boolean)

    show_attributes = Column(Boolean)
    show_instances = Column(Boolean)
    show_userscripts = Column(Boolean)
    show_nav_bar = Column(Boolean)
    show_left_bar = Column(Boolean)

    style_complete_button = Column(String())

    background_color = Column(String())

    # label_settings
    settings_enable_snap_to_instance = Column(Boolean)
    settings_show_ghost_instances = Column(Boolean)
    settings_show_text = Column(Boolean)
    settings_show_label_text = Column(Boolean)
    settings_show_attribute_text = Column(Boolean)
    settings_show_list = Column(Boolean)
    settings_show_occluded_keypoints = Column(Boolean)
    settings_allow_multiple_instance_select = Column(Boolean)
    settings_font_size = Column(Integer)
    settings_spatial_line_size = Column(Integer)
    settings_vertex_size = Column(Integer)
    settings_font_background_opacity = Column(Integer)
    settings_show_removed_instances = Column(Boolean)
    settings_target_reticle_size = Column(Integer)
    settings_filter_brightness = Column(Integer)
    settings_filter_contrast = Column(Integer)
    settings_filter_grayscale = Column(Integer)
    settings_instance_buffer_size = Column(Integer)
    settings_canvas_scale_global_is_automatic = Column(Boolean)
    settings_canvas_scale_global_setting = Column(Float)
    settings_left_nav_width = Column(Integer)
    settings_on_instance_creation_advance_sequence = Column(Boolean)
    settings_ghost_instances_closed_by_open_view_edit_panel = Column(Boolean)

    allowed_instance_type_list = Column(ARRAY(String()))
    allowed_instance_template_id_list = Column(ARRAY(Integer()))

    allow_instance_delete = Column(Boolean)
    allow_instance_move = Column(Boolean)
    allow_new_instance_creation = Column(Boolean)
    allow_new_instance_creation = Column(Boolean)
    allow_label_change = Column(Boolean)
    allow_attribute_change = Column(Boolean)
    allow_copy_paste = Column(Boolean)
    allow_new_template_creation = Column(Boolean)
    allow_history_access = Column(Boolean)

    allow_edit_of_complete_task = Column(Boolean)

    default_to_view_only_mode = Column(Boolean)
    default_to_qa_slideshow = Column(Boolean)


    def serialize(self):
        # https://github.com/n0nSmoker/SQLAlchemy-serializer
        return self.to_dict()


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
                name_search = "%{}%".format(name)
                query = query.filter(UI_Schema.name.ilike(name_search))
            else:
                query = query.filter(UI_Schema.name == name)

        if date_from or date_to:
            if date_from:
                query = query.filter(UI_Schema.created_time >= date_from)
            if date_to:
                query = query.filter(UI_Schema.created_time <= date_to)
        else:
            query = regular_methods.regular_query(
                query=query,
                date_from_string=date_from_string,
                date_to_string=date_to_string,
                base_class=UI_Schema,
                created_time_string='time_updated'
            )

        if archived is False:   
            query = query.filter(UI_Schema.archived == False)

        if order_by_class_and_attribute:
            query = query.order_by(
                nullslast(order_by_direction(order_by_class_and_attribute)))

        if return_kind == "count":
            return query.limit(limit).count()

        if return_kind == "objects":
            return query.limit(limit).all()


    @staticmethod
    def new(
            member: 'Member' = None,
            project: 'Project' = None,
            client_created_time = None,
            client_creation_ref_id = None,
            name = None
            ) -> 'UI_Schema':

        print("kwargs", kwargs)
        return UI_Schema(kwargs)   
