# OPENCORE - ADD
from shared.database.common import *
from sqlalchemy.orm.session import Session
import hashlib
import json
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from werkzeug.exceptions import Forbidden
from shared.database.text_file import TextFile
from shared.database.point_cloud.point_cloud import PointCloud
from shared.database.audio.audio_file import AudioFile
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
from sqlalchemy import Time
logger = get_shared_logger()

from sqlalchemy.schema import Index


class FileAnnotations(Base, Caching):
    """
        This is an aggregate table that relates the label_file ID and attributes ID
        with a file ID.
    """

    __tablename__ = 'file_annotations'

    __table_args__ = (
        Index('index__video_parent_file_id__and__frame_number',
              "video_parent_file_id",
              "frame_number"),
    )

    id = Column(BIGINT, primary_key = True)
    created_time = Column(DateTime, default = datetime.datetime.utcnow)

    # Number of instances (Of all types) in the file.
    count_instances = Column(Integer, default = None, nullable = True)

    file_id = Column(Integer, ForeignKey('file.id'))
    file = relationship("File")

    label_file_id = Column(Integer, ForeignKey('file.id'))
    label_file = relationship("File")

    annotators_member_list = Column(ARRAY(Integer), nullable = True, default = [])

    attribute_value_text = Column(String, nullable = True)

    attribute_value_selected = Column(Boolean, nullable = True)

    attribute_value_selected_date = Column(DateTime, nullable = True)

    attribute_value_selected_time = Column(Time, nullable = True)

    # The Option Selected for cases where there are options to select. (treeview, radio, select)
    attribute_template_id = Column(Integer, ForeignKey('attribute_template.id'))

    # The Attribute Type ID (Multi Select, radio, checkbox, etc..)
    attribute_template_group_id = Column(Integer, ForeignKey('attribute_template_group.id'))

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    @staticmethod
    def new(session: Session,
            file_id: int,
            label_file_id: int,
            count_instances: int,
            annotators_member_list: list,
            attribute_value_text: str = None,
            attribute_value_selected: bool = None,
            attribute_value_selected_date: datetime.datetime = None,
            add_to_session: bool = True,
            flush_session: bool = True):

        file_annotation = FileAnnotations(
            file_id = file_id,
            label_file_id = label_file_id,
            count_instances = count_instances,
            annotators_member_list = annotators_member_list,
            attribute_value_text = attribute_value_text,
            attribute_value_selected = attribute_value_selected,
            attribute_value_selected_date = attribute_value_selected_date
        )

        if add_to_session:
            session.add(file_annotation)

        if flush_session:
            session.flush()

        return file_annotation

    @staticmethod
    def update_file_annotations_data(session: Session, instance_list: list, file_id: int):
        # First Delete existing
        session.query(FileAnnotations).filter(
            FileAnnotations.file_id == file_id
        ).delete()
        members_list = []

        # Build label count entries based on instance list
        label_counts = {}
        for instance in instance_list:
            label_file_id = instance['label_file_id']
            if label_counts.get(label_file_id):
                label_counts[label_file_id] += 1
            else:
                label_counts[label_file_id] = 1
            members_list.append(instance['member_created_id'])

        for key, val in label_counts.items():
            file_annotation = FileAnnotations.new(
                session = session,
                file_id = file_id,
                label_file_id = key,
                count_instances = val,
            )

        # Build Attribute Entries
        for instance in instance_list:
            for attribute_groups in instance_list.get('attribute_groups'):
                if attribute_groups is None:
                    continue
                print('attributeee', attribute_groups)
                for key, val in attribute_groups.items():
                    value, type = get_tree_attribute_value(key, val)


