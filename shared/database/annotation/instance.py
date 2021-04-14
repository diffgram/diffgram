# OPENCORE - ADD
from shared.database.common import *
import shared.data_tools_core as data_tools_core
import hashlib
import json
from sqlalchemy.schema import Index


class Instance(Base):
    """
    An individual annotation instance

    """
    __tablename__ = 'instance'

    id = Column(BIGINT, primary_key = True)
    previous_id = Column(BIGINT)
    next_id = Column(BIGINT)
    root_id = Column(BIGINT, index = True)
    version = Column(Integer, default = 0)

    created_time = Column(DateTime, default = datetime.datetime.utcnow)
    last_updated_time = Column(DateTime, onupdate = datetime.datetime.utcnow)
    client_created_time = Column(DateTime, nullable = True)
    deleted_time = Column(DateTime, nullable = True)

    # Used to explain why the instance was deleted, currently 2 cases:
    # system: means that the instance was deleted by the version control system, any type of edit trigger this type.
    # user: means that the user purposefully deleted the instance
    # null: usually this value is on the "most recent" instance version ie, no delete actions after it.
    deletion_type = Column(String, nullable = True)

    # For defining the type of action that happened to the instance when it changed (edited, deleted, created, etc)
    action_type = Column(String, nullable = True)

    # For knowing the source of the update (SDK/Frontend, Third Party, ectc)
    change_source = Column(String, nullable = True)

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project")

    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", foreign_keys = [task_id])

    type = Column(String())  # "box", "polygon", "tag", "text_token" ...
    hash = Column(String())

    # TODO clarify what status was for
    status = Column(String())

    start_sentence = Column(Integer())
    end_sentence = Column(Integer())

    start_token = Column(Integer())
    end_token = Column(Integer())

    start_char = Column(Integer())
    end_char = Column(Integer())
    sentence = Column(Integer())

    # Keyframe list?

    # ie for video
    sequence_id = Column(Integer, ForeignKey('sequence.id'))
    sequence = relationship("Sequence")
    # Has changes?

    # Instance sequence features
    # Ie this is the 2nd car in the image
    number = Column(Integer)
    frame_number = Column(Integer)

    global_frame_number = Column(Integer)

    # TODO review interpolated
    # And other options in relation to say box
    machine_made = Column(Boolean)
    interpolated = Column(Boolean)

    # Should this be machine_made_type?
    fan_made = Column(Boolean)

    verified = Column(Boolean)

    #  this is part of attributes now, delete?
    # TODO, do we want user selectable bools?
    occluded = Column(String())  # "full", "partial" ...
    # Other?

    soft_delete = Column(Boolean)  # This is just for working dir

    # Should this actually be label id or label file id?
    label_file_id = Column(Integer, ForeignKey('file.id'))
    label_file = relationship("File", foreign_keys = [label_file_id])

    parent_file_id = Column(Integer, ForeignKey('file.id'))
    parent_file = relationship("File", foreign_keys = [parent_file_id])

    file_id = Column(Integer, ForeignKey('file.id'))
    file = relationship("File", back_populates = "instance_list",
                        foreign_keys = [file_id])

    is_template = Column(Boolean, default = False)
    # Kepoints features:
    nodes = Column(MutableDict.as_mutable(JSONEncodedDict),
                    default = {'nodes': []})
    edges = Column(MutableDict.as_mutable(JSONEncodedDict),
                    default = {'edges': []})
    # Polygon features:
    # points.points = list of points, point = {x : value, y: value}
    points = Column(MutableDict.as_mutable(JSONEncodedDict),
                    default = {'points': []})

    mask_url = Column(String())
    mask_blob_dir = Column(MutableDict.as_mutable(JSONEncodedDict),
                           default = {'list': []})
    mask_url_expiry = Column(Integer)

    # Box (may be used for polygon too)
    x_min = Column(Integer)
    y_min = Column(Integer)
    x_max = Column(Integer)
    y_max = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)

    # For Ellipse Instances
    center_x = Column(Integer)
    center_y = Column(Integer)
    angle = Column(Float)  # For ellipse rotation, and probably other instance in the future

    # Bezier curve [quadratic]
    p1 = Column(MutableDict.as_mutable(JSONEncodedDict))  # point 1
    p2 = Column(MutableDict.as_mutable(JSONEncodedDict))  # point 2
    cp = Column(MutableDict.as_mutable(JSONEncodedDict))  # Control point


    front_face = Column(MutableDict.as_mutable(JSONEncodedDict))

    rear_face = Column(MutableDict.as_mutable(JSONEncodedDict))

    # CAREFUL renamed these
    preview_image_url = Column(String())
    preview_image_blob_dir = Column(String())
    preview_image_url_expiry = Column(Integer)

    # Unique reference for creating an instance. Can be useful for updating frontend interfaces when new instances
    # are added but no ID is available. This is value that is generated by the client and not by the backend.
    creation_ref_id = Column(String(), nullable = True)

    rating = Column(Integer)

    rating_comment = Column(String())

    attribute_groups = Column(MutableDict.as_mutable(JSONEncodedDict))

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])


    __table_args__ = (
        Index('index__file_id__and__frame_number',
              "file_id", "frame_number"),
        Index('index__sequence_id__and__soft_delete',
              "sequence_id", "soft_delete"
              ),
    )

    @staticmethod
    def get_child_instance_history(session, root_id):
        root = session.query(Instance).filter(Instance.id == root_id).first()

        history_list = session.query(Instance).filter(
            Instance.root_id == root_id
        ).order_by(Instance.version.desc()).all()

        if root not in history_list:
            history_list.append(root)
            return history_list
        else:
            return history_list


    @staticmethod
    def get_by_id(session, instance_id):
        instance = session.query(Instance).filter(Instance.id == instance_id).first()
        return instance


    @staticmethod
    def list(
            session,
            file_id = None,
            label_file_id = None,
            sequence_id = None,
            exclude_removed = True,
            number = None,
            limit = 100,
            return_kind = "objects",
            date_to = None,
            date_from = None,
            frame_number = None
    ):
        """

        If we have a file id, then can use it directly instead of
        having to get file object first?

        date_from / date_to expects a type datetime object?
        """

        if not file_id and not sequence_id:
            return False

        # Base Query
        query = session.query(Instance)
        
        if file_id:
            query = query.filter(Instance.file_id == file_id)

        if label_file_id:
            query = query.filter(Instance.label_file_id == label_file_id)

        if sequence_id:
            query = query.filter(Instance.sequence_id == sequence_id)

        if frame_number is not None:
            query = query.filter(Instance.frame_number == frame_number)

        if exclude_removed is True:
            query = query.filter(Instance.soft_delete != True)

        if number is not None:
            query = query.filter(Instance.number == number)

        datetime_property = Instance.created_time

        if date_from and date_to:
            query = query.filter(
                datetime_property >= date_from,
                datetime_property <= date_to)
        else:
            if date_from:
                query = query.filter(datetime_property >= date_from)

            if date_to:
                query = query.filter(datetime_property <= date_to)

        if limit:
            query = query.limit(limit)

        if return_kind == "query":
            return query

        if return_kind == "count":
            return query.count()

        if return_kind == "objects":
            return query.all()


    def do_soft_delete(self) -> None:
        """
        Context of wanting to hash afterwards

        Caution, need to set cache dirty (especially for video)
        otherwise won't update...
            We don't know what other instances might be effected
            so can't regenerate cache directly here

        TODO hash and set file key could maybe be part of some
        shared concept for per instance changes

        """

        self.soft_delete = True
        self.hash_instance()
        self.file.set_cache_key_dirty(cache_key = 'instance_list')


    def hash_instance(self) -> None:
        """
        Important -> Used in core annotation saving function

        Must call if we do any updates to an instance

        It's ok if this has None values,
        it should be the same for all instance types

        I wonder if this should be part of a default method for instance itself?
        Feels almost like a serialization thing.

        Updates in place

        CAUTION
        anything we add here must be "static".
        if we add a datetime it will create an infinite loop
        since every instance will be "new".

        """
        assert self.label_file_id is not None

        hash_data = [
            self.type,
            self.x_min,
            self.y_min,
            self.y_max,
            self.x_max,
            self.p1,
            self.p2,
            self.cp,
            self.center_x,
            self.center_y,
            self.angle,
            self.width,
            self.height,
            self.start_char,
            self.end_char,
            self.start_token,
            self.end_token,
            self.start_sentence,
            self.end_sentence,
            self.sentence,
            self.label_file_id,
            self.number,
            self.rating,
            self.points,
            self.front_face,
            self.rear_face,
            self.soft_delete,
            self.attribute_groups,
            self.machine_made,
            self.sequence_id
        ]

        self.hash = hashlib.sha256(json.dumps(
            hash_data, sort_keys = True).encode('utf-8')).hexdigest()

    """
    WIP would like to send less information per instance
    (ie just the label_file_id) but need to build stronger 
    label map / other stuff there.
    """
    def serialize_with_member_data(self):
        result = self.serialize()
        if self.member_created and self.member_created.user:
            result['member_created'] = self.member_created.user.serialize_public()
        return result

    def serialize(self):

        # may be None if object hasn't been fully created yet
        # context of serializing for preview in buffer
        points = None
        if self.points:
            points = self.points.get('points', None)

        nodes = None
        if self.nodes:
            nodes = self.nodes.get('nodes', None)

        edges = None
        if self.edges:
            edges = self.edges.get('edges', None)

        return {
            'id': self.id,
            'type': self.type,
            'file_id': self.file_id,
            'label_file_id': self.label_file_id,
            'soft_delete': self.soft_delete,
            'x_min': self.x_min,
            'y_min': self.y_min,
            'x_max': self.x_max,
            'y_max': self.y_max,
            'deletion_type': self.deletion_type,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'action_type': self.action_type,
            'deleted_time': self.deleted_time.isoformat() if self.deleted_time else None,
            'change_source': self.change_source,
            'p1': self.p1,
            'p2': self.p2,
            'cp': self.cp,
            'center_x': self.center_x,
            'center_y': self.center_y,
            'angle': self.angle,
            'creation_ref_id': self.creation_ref_id,
            'width': self.width,
            'height': self.height,
            'number': self.number,
            'interpolated': self.interpolated,
            'machine_made': self.machine_made,
            'sequence_id': self.sequence_id,
            'fan_made': self.fan_made,
            'points': points,
            'front_face': self.front_face,
            'rear_face': self.rear_face,
            'rating': self.rating,
            'attribute_groups': self.attribute_groups,
            'member_created_id': self.member_created_id,
            'previous_id': self.previous_id,
            'next_id': self.next_id,
            'root_id': self.root_id,
            'version': self.version,
            'nodes': nodes,
            'edges': edges

        }


    def serialize_with_label(self):

        instance = self.serialize()

        label_file = None
        if self.label_file is not None:
            label_file = self.label_file.serialize_with_label()

        instance['label_file'] = label_file
        return instance


    def serialize_for_source_control(self):
        label_file = None
        if self.label_file is not None:
            label_file = self.label_file.serialize_with_label()

        return {
            'id': self.id,
            'type': self.type,
            'file_id': self.file_id,
            'label_file': label_file,
            'soft_delete': self.soft_delete,
            'creation_ref_id': self.creation_ref_id,
            'x_min': self.x_min,
            'y_min': self.y_min,
            'center_x': self.center_x,
            'center_y': self.center_y,
            'angle': self.angle,
            'x_max': self.x_max,
            'y_max': self.y_max,
            'p1': self.p1,
            'p2': self.p2,
            'cp': self.cp,
            'width': self.width,
            'height': self.height,
            'number': self.number,
            'fan_made': self.fan_made,
            'sequence_id': self.sequence_id,
            'points': self.points.get('points', None),
            'front_face': self.front_face,
            'rear_face': self.rear_face,
            'rating': self.rating,
            'attribute_groups': self.attribute_groups,
            'member_created_id': self.member_created_id,
            'previous_id': self.previous_id,
            'next_id': self.next_id,
            'root_id': self.root_id,
            'version': self.version
        }

    # TODO revist in context of new instance structure
    def serialize_for_activity(self):
        return {
            'id': self.id,
            'x_min': self.x_min,
            'y_min': self.y_min,
            'x_max': self.x_max,
            'y_max': self.y_max,
            'p1': self.p1,
            'p2': self.p2,
            'cp': self.cp,
            'center_x': self.center_x,
            'center_y': self.center_y,
            'angle': self.angle,
            'front_face': self.front_face,
            'rear_face': self.rear_face,
            'file_id': self.file_id,
            'creation_ref_id': self.creation_ref_id,
            'width': self.width,
            'height': self.height,
            'annotations_are_machine_made': self.annotations_are_machine_made,
            'status': self.status,
            'interpolated': self.interpolated,
            'previous_id': self.previous_id,
            'next_id': self.next_id,
            'root_id': self.root_id,
            'version': self.version
        }

    def serialize_for_sequence_preview(self, session):
        data_tools = data_tools_core.Data_tools().data_tools
        """
        preview_image_url = Column(String())
        preview_image_blob_dir = Column(String())
        preview_image_url_expiry = Column(Integer)

        TODO feel like this should be a more regular pattern...
        Since we have signed URL in other stuff...

        Feb 7, 2020
        add check for preview_image_blob_dir
        because if it's None it will hit the fail everytime
        and this route can get heavy enough as is 
        just a little thing as saw a bunch of print statments repeating

        Also bug fix if it suceeds to update time properly.
        """

        if self.preview_image_blob_dir:
            if self.preview_image_url_expiry is None or \
                    self.preview_image_url_expiry <= time.time():

                try:
                    self.preview_image_url = data_tools.build_secure_url(path = self.preview_image_blob_dir)
                    self.preview_image_url_expiry = time.time() + 2591000
                    session.add(self)
                except:
                    print("serialize_for_sequence_preview build_secure_url failed, preview_image_blob_dir: ",
                          self.preview_image_blob_dir)

        return {
            'id': self.id,
            'file_id': self.file_id,
            'preview_image_url': self.preview_image_url
        }
