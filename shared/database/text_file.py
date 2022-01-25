# OPENCORE - ADD
from shared.database.common import *
from shared.database.common import data_tools
from shared.settings import settings


class TextFile(Base):
    __tablename__ = 'text_file'

    id = Column(BIGINT, primary_key = True)

    original_filename = Column(String(250))
    description = Column(String(250))

    soft_delete = Column(Boolean, default = False)

    mask_joint_url = Column(String())
    mask_joint_blob_name = Column(String())

    is_inference = Column(Boolean, default = False)

    annotation_status = Column(String())  # "complete" "init" "in_progress" ?

    is_annotation_example = Column(Boolean, default = False)
    url_annotation_example = Column(String())

    url_public = Column(String())

    url_signed = Column(String())
    url_signed_blob_path = Column(String())

    url_signed_expiry = Column(Integer)

    tokens_url_signed = Column(String())
    tokens_url_signed_blob_path = Column(String())

    tokens_url_signed_expiry = Column(Integer)

    url_signed_expiry_force_refresh = Column(Integer)
    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    def get_text(self):
        """
            Download Raw text from blob.
        :return:
        """

    def get_by_id(session, id):
        return session.query(TextFile).filter(TextFile.id == id).first()

    # For annotation assignments
    def serialize_for_example(self):
        text = {
            'is_annotation_example': self.is_annotation_example,
            'url_annotation_example': self.url_annotation_example,
            'url_annotation_example_thumb': self.url_annotation_example_thumb
        }
        return text

    def serialize(self):

        keyframe = False

        text = {
            'original_filename': self.original_filename,
            'soft_delete': self.soft_delete,
            'url_signed': self.url_signed,
            'id': self.id,
            'is_inference': self.is_inference,
            'tokens_url_signed': self.tokens_url_signed,
            'is_annotation_example': self.is_annotation_example,
            'annotation_status': self.annotation_status
        }
        return text

    def serialize_for_source_control(self, session = None):

        if session:

            # TODO not a fan of how many conditions we are checking here...
            if self.url_signed_expiry is None or self.url_signed_expiry <= time.time():
                data_tools.rebuild_secure_urls_image(session, self)

            if self.url_signed_expiry_force_refresh is None or \
                self.url_signed_expiry_force_refresh != settings.URL_SIGNED_REFRESH:  # Handle purposefully triggering a reset

                self.url_signed_expiry_force_refresh = settings.URL_SIGNED_REFRESH

                data_tools.rebuild_secure_urls_image(
                    session, self)

        return {
            'original_filename': self.original_filename,
            'soft_delete': self.soft_delete,
            'url_signed': self.url_signed,
            'tokens_url_signed': self.tokens_url_signed,
            'annotation_status': self.annotation_status
        }

    def regenerate_tokens_urls(self, session):
        """
            Refresh signed URL for tokens Blob of the text file.
        :param session:
        :return:
        """
        if session and self.tokens_url_signed_blob_path:

            # We assume a significant delta between minimum days
            # and new offset (ie at least 10 minutes)
            minimum_days_valid = 30 * 12  # this should always be lower then new offset
            new_offset_days_valid = 30 * 14
            time_to_check = time.time() + (86400 * minimum_days_valid)

            if self.tokens_url_signed_expiry is None or self.tokens_url_signed_expiry <= time_to_check:
                new_offset_in_seconds = 86400 * new_offset_days_valid

                self.tokens_url_signed = data_tools.build_secure_url(self.tokens_url_signed_blob_path, new_offset_in_seconds)
                self.tokens_url_signed_expiry = time.time() + new_offset_in_seconds
                session.add(self)

    def regenerate_url(self, session):
        """
            Refresh signed URL for the raw Text blob.
        :param session:
        :return:
        """
        if session and self.url_signed_blob_path:

            # We assume a significant delta between minimum days
            # and new offset (ie at least 10 minutes)
            minimum_days_valid = 30 * 12  # this should always be lower then new offset
            new_offset_days_valid = 30 * 14
            time_to_check = time.time() + (86400 * minimum_days_valid)

            if self.url_signed_expiry is None or self.url_signed_expiry <= time_to_check:
                new_offset_in_seconds = 86400 * new_offset_days_valid

                self.url_signed = data_tools.build_secure_url(self.url_signed_blob_path, new_offset_in_seconds)
                self.url_signed_expiry = time.time() + new_offset_in_seconds
                session.add(self)

        self.regenerate_tokens_urls(session)
