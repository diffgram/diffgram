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
from shared.utils.attributes.attributes_values_parsing import get_attribute_value
from shared.database.project import Project
logger = get_shared_logger()

from sqlalchemy.schema import Index


class FileStats(Base, Caching):
    """
        This is an aggregate table that relates the label_file ID and attributes ID
        with a file ID.
    """

    __tablename__ = 'file_stats'

    id = Column(BIGINT, primary_key = True)
    created_time = Column(DateTime, default = datetime.datetime.utcnow)

    # Number of instances (Of all types) in the file.
    count_instances = Column(Integer, default = None, nullable = True)

    file_id = Column(Integer, ForeignKey('file.id'))
    file = relationship("File", foreign_keys = [file_id])

    label_file_id = Column(Integer, ForeignKey('file.id'))
    label_file = relationship("File", foreign_keys = [label_file_id])

    annotators_member_list = Column(ARRAY(Integer), nullable = True, default = [])

    attribute_value_text = Column(String, nullable = True)

    attribute_value_number = Column(Integer, nullable = True)

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
            annotators_member_list: list,
            count_instances: int = None,
            attribute_value_text: str = None,
            attribute_value_selected: bool = None,
            attribute_template_id: int = None,
            attribute_template_group_id: int = None,
            attribute_value_number: int = None,
            attribute_value_selected_date: datetime.datetime = None,
            attribute_value_selected_time: time = None,
            add_to_session: bool = True,
            flush_session: bool = True):

        file_stat = FileStats(
            file_id = file_id,
            label_file_id = label_file_id,
            count_instances = count_instances,
            annotators_member_list = annotators_member_list,
            attribute_value_text = attribute_value_text,
            attribute_value_selected = attribute_value_selected,
            attribute_value_selected_date = attribute_value_selected_date,
            attribute_value_selected_time = attribute_value_selected_time,
            attribute_value_number = attribute_value_number,
            attribute_template_id = attribute_template_id,
            attribute_template_group_id = attribute_template_group_id
        )

        if add_to_session:
            session.add(file_stat)

        if flush_session:
            session.flush()

        return file_stat

    @staticmethod
    def update_file_stats_data(session: Session, instance_list: list, file_id: int, project: Project):
        # First Delete existing
        if instance_list is None:
            return
        session.query(FileStats).filter(
            FileStats.file_id == file_id
        ).delete()
        members_list = []
        # Build label count entries based on instance list
        label_counts = {}
        for instance in instance_list:
            if instance.get('soft_delete') is True:
                continue
            label_file_id = instance['label_file_id']
            if label_counts.get(label_file_id):
                label_counts[label_file_id] += 1
            else:
                label_counts[label_file_id] = 1
            if instance['member_created_id'] not in members_list:
                members_list.append(instance['member_created_id'])

        for key, val in label_counts.items():
            FileStats.new(
                session = session,
                file_id = file_id,
                label_file_id = key,
                count_instances = val,
                annotators_member_list = members_list,
            )

        # Build Attribute Entries
        for instance in instance_list:
            if not instance.get('attribute_groups'):
                continue
            if instance.get('soft_delete') is True:
                continue
            for key, val in instance.get('attribute_groups').items():
                value, attr_type = get_attribute_value(session, int(key), val, project)
                if attr_type in ['select', 'radio']:
                    FileStats.new(
                        session = session,
                        file_id = file_id,
                        label_file_id = instance['label_file_id'],
                        count_instances = None,
                        annotators_member_list = members_list,
                        attribute_value_selected = True,
                        attribute_template_id = int(value),
                        attribute_template_group_id = int(key)
                    )
                if attr_type in ['tree', 'multiple_select']:
                    for attr_template_id in value:
                        FileStats.new(
                            session = session,
                            file_id = file_id,
                            label_file_id = instance['label_file_id'],
                            count_instances = None,
                            annotators_member_list = members_list,
                            attribute_value_selected = True,
                            attribute_template_id = int(attr_template_id),
                            attribute_template_group_id = int(key)
                        )
                if attr_type in ['time']:
                    import time
                    print('AAAAA', value, type(value))
                    print('AAAAA', time.time(), type(time.time()))

                    FileStats.new(
                        session = session,
                        file_id = file_id,
                        label_file_id = instance['label_file_id'],
                        count_instances = None,
                        annotators_member_list = members_list,
                        attribute_value_selected_time = value,
                        attribute_template_group_id = int(key)
                    )
                if attr_type in ['date']:
                    FileStats.new(
                        session = session,
                        file_id = file_id,
                        label_file_id = instance['label_file_id'],
                        count_instances = None,
                        annotators_member_list = members_list,
                        attribute_value_selected_date = value,
                        attribute_template_group_id = int(key)
                    )
                if attr_type in ['slider']:
                    FileStats.new(
                        session = session,
                        file_id = file_id,
                        label_file_id = instance['label_file_id'],
                        count_instances = None,
                        annotators_member_list = members_list,
                        attribute_value_number = value,
                        attribute_template_group_id = int(key)
                    )
                if attr_type in ['text']:
                    FileStats.new(
                        session = session,
                        file_id = file_id,
                        label_file_id = instance['label_file_id'],
                        count_instances = None,
                        annotators_member_list = members_list,
                        attribute_value_text = value,
                        attribute_template_group_id = int(key)
                    )

