# OPENCORE - ADD
from shared.database.common import *
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

    label_file_id = Column(Integer, ForeignKey('file.id'))
    label_file = relationship("File")

    annotators_member_list = Column(ARRAY(Integer), nullable = True, default = [])

    attribute_value_selected = Column(String, ForeignKey('attribute.id'))

    attribute_value_selected_date = Column(String, ForeignKey('attribute.id'))

    # The Option Selected for cases where there are options to select. (treeview, radio, select)
    attribute_template_id = Column(Integer, ForeignKey('attribute_template.id'))

    # The Attribute Type ID (Multi Select, radio, checkbox, etc..)
    attribute_template_group_id = Column(Integer, ForeignKey('attribute_template_group.id'))

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])
