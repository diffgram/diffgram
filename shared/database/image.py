# OPENCORE - ADD
from shared.database.common import *
from shared.settings import settings
from shared.database.common import data_tools


class Image(Base):
    __tablename__ = 'image'

    id = Column(BIGINT, primary_key = True)

    original_filename = Column(String(250))
    description = Column(String(250))
    width = Column(Integer)
    height = Column(Integer)
    soft_delete = Column(Boolean, default = False)

    mask_joint_url = Column(String())
    mask_joint_blob_name = Column(String())

    is_inference = Column(Boolean, default = False)

    file_list = relationship("File")

    annotation_status = Column(String())  # "complete" "init" "in_progress" ?

    is_annotation_example = Column(Boolean, default = False)
    url_annotation_example = Column(String())
    url_annotation_example_thumb = Column(String())

    url_public = Column(String())
    url_public_thumb = Column(String())

    url_signed = Column(String())
    url_signed_blob_path = Column(String())

    # key assumption is that
    # rebuild_secure_urls_image() handles BOTH regular images
    # and thumbnail images...
    url_signed_thumb = Column(String())
    url_signed_thumb_blob_path = Column(String())

    url_signed_expiry = Column(Integer)

    url_signed_expiry_force_refresh = Column(Integer)
    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    def get_by_id(session, id):
        return session.query(Image).filter(Image.id == id).first()

    # For annotation assignments
    def serialize_for_example(self):
        image = {
            'width': self.width,
            'height': self.height,
            'is_annotation_example': self.is_annotation_example,
            'url_annotation_example': self.url_annotation_example,
            'url_annotation_example_thumb': self.url_annotation_example_thumb
        }
        return image

    def serialize(self):

        keyframe = False

        image = {
            'original_filename': self.original_filename,
            'width': self.width,
            'height': self.height,
            'soft_delete': self.soft_delete,
            'url_signed': self.url_signed,
            'url_signed_thumb': self.url_signed_thumb,
            'id': self.id,
            'is_inference': self.is_inference,
            'is_annotation_example': self.is_annotation_example,
            'annotation_status': self.annotation_status
        }
        return image

    def serialize_for_source_control(self, session = None):

        if session and self.url_signed_blob_path:

            if self.url_signed_expiry is None or self.url_signed_expiry <= time.time():
                data_tools.rebuild_secure_urls_image(
                    session, self)

            if self.url_signed_expiry_force_refresh is None or \
                self.url_signed_expiry_force_refresh != settings.URL_SIGNED_REFRESH:  # Handle purposefully triggering a reset

                self.url_signed_expiry_force_refresh = settings.URL_SIGNED_REFRESH

                data_tools.rebuild_secure_urls_image(
                    session, self)

        return {
            'original_filename': self.original_filename,
            'width': self.width,
            'height': self.height,
            'soft_delete': self.soft_delete,
            'url_signed': self.url_signed,
            'url_signed_thumb': self.url_signed_thumb,
            'annotation_status': self.annotation_status
        }

    def regenerate_url(self, session):
        if session and self.url_signed_blob_path:

            # We assume a significant delta between minimum days
            # and new offset (ie at least 10 minutes)
            minimum_days_valid = 30 * 12  # this should always be lower then new offset
            new_offset_days_valid = 30 * 14
            time_to_check = time.time() + (86400 * minimum_days_valid)

            if self.url_signed_expiry is None or self.url_signed_expiry <= time_to_check:
                new_offset_in_seconds = 86400 * new_offset_days_valid

                self.url_signed = data_tools.build_secure_url(self.url_signed_blob_path, new_offset_in_seconds)
                self.url_signed_thumb = data_tools.build_secure_url(self.url_signed_thumb_blob_path,
                                                                    new_offset_in_seconds)
                self.url_signed_expiry = time.time() + new_offset_in_seconds
                session.add(self)
