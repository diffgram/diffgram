# OPENCORE - ADD
from shared.database.common import *
import hashlib
import json
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from werkzeug.exceptions import Forbidden
from shared.database.text_file import TextFile
from shared.database.point_cloud.point_cloud import PointCloud
from shared.database.source_control import working_dir as working_dir_database_models
from shared.database.annotation.instance import Instance
from shared.database.labels.label import Label
from shared.database.text_file import TextFile
from shared.database.video.sequence import Sequence
from shared.helpers.sessionMaker import AfterCommitAction
from shared.database.labels.label_schema import LabelSchema
import time
from shared.regular import regular_log
from sqlalchemy.orm import joinedload
from shared.shared_logger import get_shared_logger
from shared.database.core import MutableDict
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import UniqueConstraint
from shared.database.geospatial.geo_asset import GeoAsset
from shared.helpers.performance import timeit


logger = get_shared_logger()

from sqlalchemy.schema import Index


class File(Base, Caching):
    """
    A file is raw data relation + annotation instances
        eg
        File.image
        File.video

    A file represents the lowest unit of source control data
    """

    __tablename__ = 'file'

    __table_args__ = (
        Index('index__video_parent_file_id__and__frame_number',
              "video_parent_file_id",
              "frame_number"),
    )

    id = Column(BIGINT, primary_key = True)
    created_time = Column(DateTime, default = datetime.datetime.utcnow)

    # TODO would be good to standarized the naming convention for time with other stuff
    time_last_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    # A way to disable auto update while doing migration? not 100% sure this works
    # time_last_updated = Column(DateTime)

    count_instances_changed = Column(Integer)

    # Number of instances (Of all types) in the file.
    count_instances = Column(Integer, default = None, nullable = True)

    created_by_kind = Column(String)  # 'human', 'api'

    time_committed = Column(DateTime)

    job_id = Column(Integer, ForeignKey('job.id'))
    job = relationship("Job")

    # Context of say wanting to check if a file is done processing. ie for video job.
    # Also could be useful in future to be able to "trace back" a file more easily
    # Instead of having to do reverse
    # I guess could just do query input id where file_id = file but just feels funny
    input_id = Column(Integer, ForeignKey('input.id'))

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])



    # "added", "removed", "changed"
    state = Column(String())  # for source control

    committed = Column(Boolean)

    # image, frame, video, label
    type = Column(String())

    # hash_data = [image_id, [instance-list], [n list]]
    hash = Column(String())

    # ann == annotation
    ann_is_complete = Column(Boolean)

    has_some_machine_made_instances = Column(Boolean)

    instance_type_count = Column(MutableDict.as_mutable(JSONEncodedDict))

    file_metadata = Column(MutableDict.as_mutable(JSONB))

    # Deprecated shift to instance_type_count
    boxes_count = Column(Integer, default = 0)
    boxes_machine_made_count = Column(Integer, default = 0)
    polygon_count = Column(Integer, default = 0)
    ##########

    image_id = Column(Integer, ForeignKey('image.id'))
    image = relationship("Image")

    point_cloud_id = Column(Integer, ForeignKey('point_cloud.id'))
    point_cloud = relationship(PointCloud)

    text_file_id = Column(Integer, ForeignKey('text_file.id'))
    text_file = relationship(TextFile, foreign_keys = [text_file_id])

    original_filename = Column(String())

    video_id = Column(Integer, ForeignKey('video.id'))
    video = relationship("Video")

    video_parent_file_id = Column(BIGINT, ForeignKey('file.id'))
    # CAUTION  NO video_parent_file object
    # MUST pass id directly...

    is_child_of_video = Column(Boolean)

    def video_parent_file(self, session):
        return session.query(File).filter(
            File.id == self.video_parent_file_id).first()

    label_id = Column(Integer, ForeignKey('label.id'))
    label = relationship("Label")
    ####

    # For security permissions and other lookups
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project")

    # Default task, although a file could have many tasks this can still be useful.
    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", foreign_keys = [task_id])

    frame_number = Column(Integer)  # assumed to be local
    global_frame_number = Column(Integer)

    # CAUTION in instance.py (shared/database/annotation)
    # see class Instance().list()
    # for more up to date / controlled way of doing this!!!
    instance_list = relationship("Instance", back_populates = "file",
                                 foreign_keys = "Instance.file_id")

    # Concept that the first file created, ie a new "import" is the "root"
    # So if a new file media was uploaded this would effect that...

    text_tokenizer = Column(String(), default = 'nltk')

    is_root = Column(Boolean)
    root_id = Column(BIGINT, ForeignKey('file.id'))

    # Key point that the file link is "arbitrary" but the file doesn't have to be???
    # Thinking about relaxing the requirement that a file be globally unique???

    parent_id = Column(BIGINT, ForeignKey('file.id'))  # Updated

    def previous(self, session):  # Legacy
        return session.query(File).filter(File.id == self.parent_id).first()

    def parent(self, session):
        return session.query(File).filter(File.id == self.parent_id).first()

    def child_list(self, session):
        return session.query(File).filter(File.parent_id == self.id).all()

    # Was "next_id"
    # DO we really need this?
    child_primary_id = Column(BIGINT, ForeignKey('file.id'))
    child_primary = relationship("File", uselist = False,
                                 foreign_keys = [child_primary_id])

    # For label generally (theory being we may want different colours for different
    # labels
    # example of colour {"hex": "#194d33", "hsl": {"l": 0.2, "h": 150, "s": 0.5, "a": 1},
    # "rgba": {"a": 1, "g": 77, "r": 25, "b": 51}, "hsv": {"a": 1, "h": 150, "s": 0.66, "v": 0.3}, "a": 1}
    colour = Column(MutableDict.as_mutable(JSONEncodedDict))

    # For semantic segmentation,
    mask_joint_blob_name = Column(String())

    # Warning: do not edit the cache manually. Especially for the instance list,
    # the recommended way of updating instances is by callin Annotation_Update().main and then
    # setting the cache to dirty with set_cache_key_dirty()
    cache_dict = Column(MutableDict.as_mutable(JSONEncodedDict),
                        default = {})

    # External ID's for referencing on integrations like Labelbox, Supervisely, etc.
    default_external_map_id = Column(BIGINT, ForeignKey('external_map.id'))  # TODO: add to production
    default_external_map = relationship("ExternalMap",
                                        uselist = False,
                                        foreign_keys = [default_external_map_id])

    __table_args__ = (UniqueConstraint('video_parent_file_id', 'frame_number', name = 'unique_frame_number_video'),)

    @staticmethod
    def get_files_in_project_id_name_list(session, project_id, id_or_name_list, directory_id = None):
        """
            Gets the files by the given list of ID's or original_filenames.
            Assumption on id_or_name_list is that any number will be
            considered and ID and any string a filename.
        :param session:
        :param project_id:
        :param id_or_name_list:
        :param directory_id:
        :return:
        """
        # Split into names and ID's
        id_list = []
        name_list = []
        for val in id_or_name_list:
            if type(val) == str:
                name_list.append(val)
            elif type(val) == int:
                id_list.append(val)
        if directory_id is not None:
            file_list_id_db = session.query(File) \
                .join(working_dir_database_models.WorkingDirFileLink,
                      working_dir_database_models.WorkingDirFileLink.file_id == File.id) \
                .filter(File.id.in_(id_list),
                        File.project_id == project_id,
                        working_dir_database_models.WorkingDirFileLink.working_dir_id == directory_id).all()
            file_list_name_db = session.query(File) \
                .join(working_dir_database_models.WorkingDirFileLink,
                      working_dir_database_models.WorkingDirFileLink.file_id == File.id) \
                .filter(File.original_filename.in_(name_list),
                        File.project_id == project_id,
                        working_dir_database_models.WorkingDirFileLink.working_dir_id == directory_id).all()
            return set(file_list_name_db + file_list_id_db)
        else:
            file_list_id_db = session.query(File) \
                .filter(File.id.in_(id_list),
                        File.project_id == project_id).all()
            file_list_name_db = session.query(File) \
                .filter(File.original_filename.in_(name_list),
                        File.project_id == project_id).all()
        return set(file_list_id_db + file_list_name_db)

    @staticmethod
    def get_frame_from_video(
        session,
        video_parent_file_id: int,
        frame_number: int,
        with_for_update: bool = False,
        nowait = False,
        skip_locked = False
    ):
        """
        Prefer this as static method
        as we may want to call it even if don't have parent file?
        In which case would need to check permissions ie through project?
        """
        if with_for_update:
            return session.query(File).with_for_update(nowait = nowait, skip_locked = skip_locked).filter(
                File.video_parent_file_id == video_parent_file_id,
                File.frame_number == frame_number).first()

        else:
            return session.query(File).filter(
                File.video_parent_file_id == video_parent_file_id,
                File.frame_number == frame_number).first()

    @staticmethod
    def get_frame_list_from_video(
        session,
        video_parent_file_id: int,
        frame_number_list: list,
        preload_image = True
    ):
        """
        Prefer this as static method
        as we may want to call it even if don't have parent file?
        In which case would need to check permissions ie through project?
        """

        if preload_image:
            return session.query(File).options(joinedload(File.image)).filter(
                File.video_parent_file_id == video_parent_file_id,
                File.frame_number.in_(frame_number_list)).all()
        else:
            return session.query(File).filter(
                File.video_parent_file_id == video_parent_file_id,
                File.frame_number.in_(frame_number_list)).all()

    def serialize(self):
        # Careful this is just basic stuff
        # Use serialize_with_type() for example
        return {
            'id': self.id,
            'hash': self.hash
        }

    def serialize_base_file(self):

        time_last_updated = None
        if self.time_last_updated:
            time_last_updated = self.time_last_updated.isoformat()

        return {
            'id': self.id,
            'hash': self.hash,
            'type': self.type,
            'state': self.state,
            'created_time': self.created_time.isoformat(),  # str() is to help with nesting json stuff
            'time_last_updated': time_last_updated,
            'ann_is_complete': self.ann_is_complete,
            'original_filename': self.original_filename,
            'video_id': self.video_id,
            'video_parent_file_id': self.video_parent_file_id,
            'count_instances_changed': self.count_instances_changed
        }

    def get_signed_url(self, session):
        if self.type == "image":
            if self.image:
                serialized = self.image.serialize_for_source_control(session)
                return serialized['url_signed']
        # Do we want to throw an error here? should be pretty rare no image if type image

        if self.type == "video":
            if self.video:
                self.video.regenerate_url(session, self.project)
                return self.video.file_signed_url

        if self.type == "text":
            if self.text_file:
                self.text_file.regenerate_url(session)
                return self.text_file.url_signed
        return None

    def get_blob_path(self):
        if self.type == "image":
            if self.image:
                return self.image.url_signed_blob_path
        # For video we're returning the Path to the entire video, not the first frame.
        if self.type == "video":
            if self.video:
                return self.video.file_blob_path

        if self.type == "text":
            if self.text_file:
                return self.text_file.url_signed_blob_path
        return None

    def get_child_point_cloud_file(self, session):

        file = session.query(File).filter(
            File.type == 'point_cloud_3d',
            File.parent_id == self.id
        ).first()
        return file

    def get_geo_assets(self, session) -> list:
        assets = session.query(GeoAsset).filter(
            GeoAsset.file_id == self.id
        ).all()
        return assets

    def serialize_geospatial_assets(self, session):
        assets_list = self.get_geo_assets(session)
        result = []
        for asset in assets_list:
            result.append(asset.serialize(session))
        return result

    def serialize_with_type(self,
                            session = None
                            ):

        file = self.serialize_base_file()

        if self.type == "image":
            if self.image:
                file['image'] = self.image.serialize_for_source_control(session)

        elif self.type == "video":
            if self.video:
                file['video'] = self.video.serialize_list_view(session, self.project)

        elif self.type == "text":
            if self.text_file:
                file['text'] = self.text_file.serialize(session)

        elif self.type == "geospatial":
            file['geospatial'] = {
                'layers': self.serialize_geospatial_assets(session = session)
            }

        elif self.type == "sensor_fusion":
            point_cloud_file = self.get_child_point_cloud_file(session = session)
            if point_cloud_file and point_cloud_file.point_cloud:
                file['point_cloud'] = point_cloud_file.point_cloud.serialize(session)

        elif self.type == "label":
            if session:
                label = Label.get_by_id(session, self.label_id)
            else:
                label = self.label
            #if session:
            #    file['attribute_group_list'] = Attribute_Template_Group.from_file_attribute_group_list_serialize(
            #        session = session,
            #       file_id = self.id)

            file['colour'] = self.colour
            file['label'] = label.serialize()

        return file

    def create_frame_packet_map(self, session):
        """
            Generates frame packet map dict from an existing video.
        :param session:
        :return:
        """
        if self.type != 'video':
            return

        # Load all frames with their instances
        video_frames = working_dir_database_models.WorkingDirFileLink.image_file_list_from_video(
            session = session,
            video_parent_file_id = self.id)
        frame_packet_map = {}
        for frame in video_frames:
            for instance in frame.instance_list:
                if instance.soft_delete:
                    continue
                serialized_instance = instance.serialize_for_frame_packet_map()
                if frame_packet_map.get(frame.frame_number) is None:
                    frame_packet_map[frame.frame_number] = [serialized_instance]
                else:
                    frame_packet_map[frame.frame_number].append(serialized_instance)
        return frame_packet_map

    # Placeholders from old code
    def serialize_with_video(self, session):
        return self.serialize_with_type(session)

    def serialize_with_label(self, session = None):
        return self.serialize_with_type(session)

    # Don't share colour by default, use map
    def serialize_with_label_and_colour(self, session):
        return self.serialize_with_type(session)

    def serialize_all_labels_in_attached_instance_list(self, session):

        label_list = []
        label_file_colour_map = {}

        for instance in self.instance_list:

            existing = label_file_colour_map.get(instance.label_file.id, None)

            if existing:
                continue

            label_list.append(instance.label_file.serialize_with_label_and_colour(
                session = session))
            label_file_colour_map[instance.label_file.id] = instance.label_file.colour

        return {
            'label_list': label_list,
            'label_file_colour_map': label_file_colour_map
        }

    def serialize_with_annotations(
        self,
        session = None):

        """
        Better way to do file splitting?
        Want to track the stuff in source control but may get a bit awkward
        if lots of file types...
        """
        instance_list = session.query(Instance).filter(
            Instance.file_id == self.id,
            Instance.soft_delete == False
        ).all()

        file = self.serialize_with_type(session)
        file['instance_list'] = [instance.serialize_with_label() for instance in instance_list]

        return file


    def serialize_annotations_only(self):

        return {
            'id': self.id,
            'hash': self.hash,
            'instance_list': [instance.serialize_with_label() for instance in self.instance_list]
        }

    def serialize_instance_list_only(self):
        return [instance.serialize_with_label() for instance in self.instance_list]

    # NOTE for more complex options
    # generally use WorkingDirFileLink.file_list()
    # Becuase we need to cross reference datasets

    @staticmethod
    def get_by_id(session, file_id, with_for_update = False, nowait = False, skip_locked = False):
        if with_for_update:
            return session.query(File).with_for_update(nowait = nowait, skip_locked = skip_locked).filter(
                File.id == file_id).first()

        else:
            return session.query(File).filter(File.id == file_id).first()

    def get_by_id_list(session, file_id_list):
        return session.query(File).filter(File.id.in_(file_id_list)).all()

    def hash_update(self):
        """
        Takes file
        (image + annotation HASHES)
        and hashes it

        Arguments:
            file, File object

        Uses from File()
            instance_list, list of annotation Instances

        Returns:
            hash,
            id_list_box, integer ids
            id_list_polygon

        """

        hash_data = []
        hash_data.append([self.image_id, self.video_id, self.label_id])

        hash_list_instance = build_annotation_hash_list(self.instance_list)

        hash_data = hash_data + hash_list_instance

        hash = hashlib.sha256(json.dumps(hash_data, sort_keys = True).encode('utf-8')).hexdigest()

        self.hash = hash

        return hash

    # get_by_id_and_project is defined in file_oeprations.py

    @staticmethod
    def validate_file_list(
        session,
        project_id,
        file_list: list,
        return_mode: str = "id") -> list:
        """
        TODO compare performance of this
        vs using a 'get where id matches list' method in sql alchemy

        Assumes that file_list is a dict of objects where the id key is available
        ie
        [{id: 1}, {id: 2}]

        return_modes: id, object

        """

        trusted_file_list = []

        for file_untrusted in file_list:

            untrusted_file_id = file_untrusted.get('id')

            file = File.get_by_id_and_project(
                session, project_id, untrusted_file_id)

            if file is None:
                raise Forbidden(f"File id not in project {str(untrusted_file_id)}")

            if return_mode == "id":
                trusted_file_list.append(file.id)
            elif return_mode == "object":
                trusted_file_list.append(file)

        return trusted_file_list

    # copy_file file copy
    # TODO rename this copy file ?
    @staticmethod
    def copy_file_from_existing(
        session,
        working_dir,
        existing_file,
        copy_instance_list: bool = False,
        log = regular_log.default(),
        add_link: bool = True,
        remove_link: bool = True,
        orginal_directory_id = None,
        previous_video_parent_id = None,
        sequence_map = None,
        deep_copy = False,
        defer_copy = False,
        ann_is_complete_reset = False,
        batch_id = None,
        flush_session = False,
        working_dir_id: int = None
    ):
        """
        orginal_directory_id is for Video, to get list of video files
        Should we rename to "source_directory" to keep in line of transfer thing?

        Clarify working_dir is the "target" directory?
        Don't actually need directory if not copying links

        # TODO is "update" really the right name
        if this is generally creating a new file??

        If file is video, we need to
        * Create the new video file
        * Create new files for all of it's frames


        ann_is_complete_reset
            We assume "copying" means copying the status too.
            However, for the example of tasks (and perhaps others in future)
            we assume we want to reset this status for the newly created files.

        """
        # Defer image copy is specified in the parameter.
        start_time = time.time()

        if working_dir:
            working_dir_id = working_dir.id

        # IMAGE Defer
        if existing_file.type == 'image' and defer_copy and not remove_link:
            regular_methods.transmit_interservice_request_after_commit(
                session = session,
                message = 'image_copy',
                logger = logger,
                service_target = 'walrus',
                id = existing_file.id,
                project_string_id = existing_file.project.project_string_id,
                extra_params = {'file_id': existing_file.id,
                                'copy_instance_list': copy_instance_list,
                                'destination_working_dir_id': working_dir_id,
                                'source_working_dir_id': orginal_directory_id,
                                'add_link': add_link,
                                'batch_id': batch_id,
                                'remove_link': remove_link,
                                }
            )
            log['info'][
                'message'] = 'File copy in progress. Please check progress in the file operations progress section.'
            return

        # VIDEO
        if existing_file.type == "video" and defer_copy is True:
            # Defer the copy to the walrus.
            regular_methods.transmit_interservice_request_after_commit(
                session = session,
                message = 'video_copy',
                logger = logger,
                service_target = 'walrus',
                id = existing_file.id,
                project_string_id = existing_file.project.project_string_id,
                extra_params = {
                    'file_id': existing_file.id,
                    'copy_instance_list': copy_instance_list,
                    'destination_working_dir_id': working_dir_id,
                    'source_working_dir_id': orginal_directory_id,
                    'add_link': add_link,
                    'batch_id': batch_id,
                    'remove_link': remove_link,
                    'frame_count': existing_file.video.frame_count
                }
            )
            log['info'][
                'message'] = 'File copy in progress. Please check progress in the file operations progress section.'
            return

        file = new_file_database_object_from_existing(session)
        file.type = existing_file.type

        # We need this to do permissions
        # At the moment when a video is done
        # We only move the video into the directory not the images
        # So we need to use the project scope.
        file.project_id = existing_file.project_id

        file.image_id = existing_file.image_id
        file.label_id = existing_file.label_id
        file.video_id = existing_file.video_id
        file.global_frame_number = existing_file.global_frame_number
        file.colour = existing_file.colour
        file_relationship(session, file, existing_file)
        file.state = "changed"
        file.frame_number = existing_file.frame_number  # Ok if None

        if ann_is_complete_reset is False:
            file.ann_is_complete = existing_file.ann_is_complete

        file.original_filename = existing_file.original_filename

        # Want to be able to get video file from anyframe...
        # Careful this is the previous one, if we just copy existing then images will
        # be related to old file
        file.video_parent_file_id = previous_video_parent_id

        session.add(file)

        # Question why does add link ned to be true here? or does it?
        # At the moment we don't pass add_link as True when copying it for task
        if add_link is True:
            working_dir_database_models.WorkingDirFileLink.add(session, working_dir_id, file)

        if remove_link is True:
            working_dir_database_models.WorkingDirFileLink.remove(session, working_dir_id, existing_file.id)

        logger.debug(f"existing_file.type {existing_file.type}")
        logger.debug(f"copy_instance_list {copy_instance_list}")
        if existing_file.type in ['image', 'frame'] and copy_instance_list is True:

            file.count_instances_changed = existing_file.count_instances_changed
            file.set_cache_key_dirty('instance_list')

            instance_list = Instance.list(
                session = session,
                file_id = existing_file.id,
                limit = None)  # Excludes removed by default
            logger.debug(f"instance_list len {len(instance_list)}")
            for instance in instance_list:

                instance_sequence_id = instance.sequence_id
                if sequence_map is not None:
                    logger.debug(f"sequence_map {sequence_map}")
                    instance_sequence_id = sequence_map.get(instance_sequence_id)

                new_instance = Instance(
                    file_id = file.id,  # IMPORTANT and different from pattern
                    sequence_id = instance_sequence_id,  # Different
                    parent_file_id = file.video_parent_file_id,  # Cache for video parent file ID.
                    project_id = instance.project_id,
                    x_min = instance.x_min,
                    y_min = instance.y_min,
                    x_max = instance.x_max,
                    y_max = instance.y_max,
                    width = instance.width,
                    height = instance.height,
                    label_file_id = instance.label_file_id,
                    hash = instance.hash,
                    type = instance.type,
                    number = instance.number,
                    frame_number = instance.frame_number,
                    global_frame_number = instance.global_frame_number,
                    machine_made = instance.machine_made,
                    fan_made = instance.fan_made,
                    points = instance.points,
                    soft_delete = instance.soft_delete,
                    center_x = instance.center_x,
                    center_y = instance.center_y,
                    angle = instance.angle,
                    p1 = instance.p1,
                    p2 = instance.p2,
                    cp = instance.cp,
                    interpolated = instance.interpolated,
                    front_face = instance.front_face,
                    rear_face = instance.rear_face,
                    creation_ref_id = instance.creation_ref_id
                )
                session.add(new_instance)

        end_time = time.time()
        if flush_session:
            session.flush()
        return file

    @staticmethod
    def new_label_file(
        session,
        name = None,
        working_dir_id = None,
        colour = None,
        project = None,
        log = None,
        existing_file = None
    ):
        label = Label.new(
            session = session,
            name = name)

        if not label:
            return None
        if existing_file is None:
            file = File.new(session = session,
                            file_type = "label",
                            working_dir_id = working_dir_id,
                            label_id = label.id,
                            colour = colour,
                            project_id = project.id
                            )
        session.flush()

        # In the future this could handle other label caching
        # Things beyond id, so for now just hit this?
        project.refresh_label_dict(session)

        if not file:
            log['error']['file'] = 'Error attaching labelfile to label'
            return None

        if project.directory_default.label_file_colour_map is None:
            project.directory_default.label_file_colour_map = {}

        project.directory_default.label_file_colour_map[file.id] = file.colour
        session.add(project)
        return file

    @staticmethod
    def new(session,
            working_dir_id = None,
            project_id = None,
            file_type = None,
            image_id = None,
            point_cloud_id = None,
            text_file_id = None,
            video_id = None,
            frame_number = None,
            label_id = None,
            colour = None,
            original_filename = None,
            video_parent_file = None,
            text_tokenizer = None,
            input_id = None,
            parent_id = None,
            task = None,
            file_metadata = None
            ):
        """
        "file_added" case

        Given a new image create a new file to track this image
        This assumes a new image is completely new

        We are always creating a new file at init so there will be A
        file, question is if there is a previous file too

        It was confusing it to have two different ways to assign project here
        so remove in favour of just having one.

        Careful with object.id, since if the object can be None it
        won't work as expected then...


        video_parent_file_id issue
            video_parent_file (not id ) FAILs because it
            does NOT exist, we have it as a function
            due to a work around issue with sql alchemy
            so MUST store the actual id

        """
        from shared.database.source_control.working_dir import WorkingDirFileLink

        video_parent_file_id = None
        if video_parent_file:
            video_parent_file_id = video_parent_file.id

        file = File(
            original_filename = original_filename,
            image_id = image_id,
            point_cloud_id = point_cloud_id,
            state = "added",
            type = file_type,
            project_id = project_id,
            label_id = label_id,
            text_file_id = text_file_id,
            video_id = video_id,
            video_parent_file_id = video_parent_file_id,
            frame_number = frame_number,
            colour = colour,
            input_id = input_id,
            parent_id = parent_id,
            task = task,
            file_metadata = file_metadata,
            text_tokenizer = text_tokenizer
        )

        File.new_file_new_frame(file, video_parent_file)

        session.add(file)
        session.flush()

        # Question do we still need to be running this here?
        file.hash_update()

        # Video frames don't need a working dir?
        # Or should we still put them in anyway...
        # in context of video frames
        # we don't want them to be in a working directory directly
        # so we can smoothly move files
        if working_dir_id:
            WorkingDirFileLink.add(session, working_dir_id, file)

        return file

    @staticmethod
    def new_file_new_frame(file, video_parent_file):
        """
        We don't have to return file as it's in session right?

        """

        if file.type == "frame":

            if not video_parent_file:
                return

            # start_time = time.time()
            video = video_parent_file.video

            if video:
                # A new file would never have this created prior...
                file.global_frame_number = video.calculate_global_reference_frame(
                    frame_number = file.frame_number)
            else:
                print("Error, no .Video while trying to create new File")

    # print("global frame cal", (time.time() - start_time) * 1000)

    # TODO review performance of this
    # Vs querrying WorkingDirFileLink directly
    # I think WorkingDirFileLink might be faster
    # And for this type of query would be functionally the same
    # Since we are just conditioning on the dir_id and the file_id
    # This would only give use the WorkingDirFileLink we would need a second
    # query to get the File

    @staticmethod
    def get_by_id_untrusted(session,
                            user_id,
                            project_string_id,
                            file_id,
                            directory_id = None,
                            with_for_update = False,
                            nowait = False,
                            skip_locked = False):
        """

        Even if we trust the directory (ie from project default),
        still have to check the file is in it!

        TODO make user_id and proejct_string_id optional (ie if directory is supplied?)

        This needs work but is used in a ton of places so review carefully!
        Plus want to keep as "one function" so we don't have a bunch of random checks

        """
        from shared.database.project import Project
        from shared.database.source_control.working_dir import WorkingDirFileLink

        if not directory_id:
            project = Project.get(session, project_string_id)
            # start_time = time.time()
            working_dir = project.directory_default
            directory_id = working_dir.id

        working_dir_sub_query = session.query(WorkingDirFileLink).filter(
            WorkingDirFileLink.working_dir_id == directory_id).subquery('working_dir_sub_query')

        if with_for_update:
            file = session.query(File).with_for_update(nowait = nowait, skip_locked = skip_locked).filter(
                File.id == working_dir_sub_query.c.file_id,
                File.id == file_id).first()
        else:
            file = session.query(File).filter(
                File.id == working_dir_sub_query.c.file_id,
                File.id == file_id).first()

        # end_time = time.time()
        # print("File access time", end_time - start_time)
        return file

    @staticmethod
    def get_by_id_and_project(
        session,
        project_id: int,
        file_id: int,
        directory_id = None,
        with_for_update = False,
        nowait = False,
        skip_locked = False):
        """
        Security models is that if the file matches the project
        (assumes that project_id is trusted), then the file has
        permission to return

        As a migration if directory_default_id is included
        will use project default directory...
        """
        if with_for_update:
            file = session.query(File).with_for_update(nowait = nowait, skip_locked = skip_locked).filter(
                File.project_id == project_id,
                File.id == file_id).first()

        else:
            file = session.query(File).filter(
                File.project_id == project_id,
                File.id == file_id).first()

        # Migration
        if not file and directory_id:
            print("used file migration")
            return File.get_by_id_and_directory_untrusted(
                session = session,
                directory_id = directory_id,
                file_id = file_id,
                with_for_update = with_for_update,
                nowait = nowait,
                skip_locked = skip_locked)

        return file

    @staticmethod
    def get_by_name_and_directory(session, directory_id, file_name):
        from shared.database.source_control.working_dir import WorkingDirFileLink
        working_dir_sub_query = session.query(WorkingDirFileLink).filter(
            WorkingDirFileLink.working_dir_id == directory_id).subquery('working_dir_sub_query')

        file = session.query(File).filter(
            File.id == working_dir_sub_query.c.file_id,
            File.original_filename == file_name).first()
        return file

    @staticmethod
    def get_by_id_and_directory_untrusted(session,
                                          directory_id,
                                          file_id,
                                          with_for_update = False,
                                          nowait = False,
                                          skip_locked = False):
        # TODO clarify the untrusted part
        # Checks that the file is in the directory / "Pulls" file from there
        # Permissions cascade from project -> directory
        from shared.database.source_control.working_dir import WorkingDirFileLink

        working_dir_sub_query = session.query(WorkingDirFileLink).filter(
            WorkingDirFileLink.working_dir_id == directory_id).subquery('working_dir_sub_query')

        if with_for_update:
            file = session.query(File).with_for_update(nowait = nowait, skip_locked = skip_locked).filter(
                File.id == working_dir_sub_query.c.file_id,
                File.id == file_id).first()

        else:
            file = session.query(File).filter(
                File.id == working_dir_sub_query.c.file_id,
                File.id == file_id).first()

        # end_time = time.time()
        # print("File access time", end_time - start_time)
        return file

    # Video and images
    def toggle_flag_shared(self,
                           session):
        """
        Basically converts the file into a video file to toggle it
        Not really happy with this "side effect"...
        careful with the "double toggle" only want to run it once...

        The reason the side effect is here is because of the awkward
        way that annotation_update() returns the frame file
        but then we actually do want to send the video file with
        the update flag... something to do but will require more testing and review...

        """

        file = self
        if file.video_parent_file_id:  # Frame file that's child of video
            # TODO use new  flag .is_child_of_video in future?
            file = file.video_parent_file(session)

        file = File.toggle_flag_single_file(session, file)

        return file

    @staticmethod
    def get_by_label_name(session, label_name, project_id):
        label_file = session.query(File).join(Label, File.label_id == Label.id).filter(
            File.project_id == project_id,
            Label.name == label_name,
            File.state == 'added'
        ).first()
        if not label_file:
            return None
        return label_file

    @staticmethod
    def __get_next_instance_and_migrate(session, video_parent_file_id, start_frame_number, label_file_id = None):
        # If there's no next frame let's retry with a join and migrate instances
        # Might eventually remove this code when all instances are migrated.
        migrate_query = session.query(Instance) \
            .join(File, Instance.file_id == File.id) \
            .filter(File.video_parent_file_id == video_parent_file_id,
                    Instance.frame_number > start_frame_number,
                    Instance.soft_delete == False)

        # If not instances with joins, then we've reached the last instance on the video.
        if migrate_query.count() == 0:
            return None

        # If there are instances, let's copy the parent file id and return the next instance.
        instances_to_update = migrate_query.all()
        for instance in instances_to_update:
            instance.parent_file_id = instance.file.video_parent_file_id
            session.add(instance)
        if label_file_id:
            migrate_query = migrate_query.filter(Instance.label_file_id == label_file_id)
        next_frame = migrate_query.order_by(Instance.frame_number).first()
        return next_frame

    @staticmethod
    def get_next_instance(session, video_parent_file_id, start_frame_number, label_file_id = None):
        query = session.query(Instance)
        query = query.filter(
            Instance.frame_number > start_frame_number,
            Instance.soft_delete == False,
            Instance.parent_file_id == video_parent_file_id
        )
        if label_file_id:
            query = query.filter(Instance.label_file_id == label_file_id)
        next_frame = query.order_by(Instance.frame_number).first()
        if next_frame:
            return next_frame

        return File.__get_next_instance_and_migrate(session,
                                                    video_parent_file_id,
                                                    start_frame_number,
                                                    label_file_id)

    @staticmethod
    def get_metadata_keys(session, project, directory = None):
        query = session.query(File).filter(
            File.project_id == project.id,
            File.state != 'removed'
        )
        if directory:
            query = query.filter(
                working_dir_database_models.WorkingDirFileLink.working_dir_id == directory.id
            )
        file_list = query.all()
        result = []
        for file in file_list:
            print(file.file_metadata, type(file.file_metadata))
            if file.file_metadata and type(file.file_metadata) == MutableDict:
                result = result + list(file.file_metadata.keys())
        return list(set(result))

    @staticmethod
    def toggle_flag_single_file(session,
                                file,
                                force_bool = None):
        assert file is not None

        session.add(file)  # not good auto adds to session.

        if force_bool:
            file.ann_is_complete = force_bool
            return file

        if file.ann_is_complete is None:
            file.ann_is_complete = True
        else:
            file.ann_is_complete = not file.ann_is_complete

        return file


def build_annotation_hash_list(annotation_list):
    hash_list = []
    for annotation in annotation_list:

        # TODO can we not just limit sql query by this?
        # Would avoid having to cycle through it here...!!
        # But we would also have to query and only return the instance hash then

        if annotation.soft_delete != True:  # for working dir only
            hash_list.append(annotation.hash)

    return hash_list


def build_annotation_hash_list_to_object(annotation_list):
    hash_list = []
    hash_to_object = {}
    for annotation in annotation_list:
        if annotation.soft_delete != True:
            hash_list.append(annotation.hash)
            hash_to_object[annotation.hash] = annotation

    return hash_list, hash_to_object


def new_file_database_object_from_existing(session):
    """
    Creates a new file object in database

    Arguments:
        session, database object


    Returns:

    """

    file = File()
    session.add(file)
    session.flush()
    return file


def file_relationship(session, file, previous_file):
    file.parent_id = previous_file.id
    if not previous_file.child_primary_id:
        previous_file.child_primary_id = file.id

    if previous_file.root_id:
        file.root_id = previous_file.root_id
    else:
        file.root_id = previous_file.id

    session.add(previous_file)
