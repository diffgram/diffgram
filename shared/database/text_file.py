# OPENCORE - ADD
from shared.database.common import *
from shared.database.common import data_tools
from shared.settings import settings



class TextFile(Base):
    __tablename__ = 'text_file'

    id = Column(BIGINT, primary_key=True)

    original_filename = Column(String(250))
    description = Column(String(250))

    soft_delete = Column(Boolean, default=False)

    mask_joint_url = Column(String())
    mask_joint_blob_name = Column(String())

    is_inference = Column(Boolean, default=False)

    annotation_status = Column(String())  # "complete" "init" "in_progress" ?

    is_annotation_example = Column(Boolean, default=False)
    url_annotation_example = Column(String())

    url_public = Column(String())

    url_signed = Column(String())
    url_signed_blob_path = Column(String())

    url_signed_expiry = Column(Integer)

    url_signed_expiry_force_refresh = Column(Integer)
    time_created = Column(DateTime, default=datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)

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
            'is_annotation_example': self.is_annotation_example,
            'annotation_status': self.annotation_status
        }
        return text

    def serialize_for_source_control(self, session=None):

        if session:

            # TODO not a fan of how many conditions we are checking here...
            if self.url_signed_expiry is None or \
                    self.url_signed_expiry <= time.time():
                data_tools.rebuild_secure_urls_image(
                    session, self)

            if self.url_signed_expiry_force_refresh is None or \
                    self.url_signed_expiry_force_refresh != settings.URL_SIGNED_REFRESH:  # Handle purposefully triggering a reset

                self.url_signed_expiry_force_refresh = settings.URL_SIGNED_REFRESH

                data_tools.rebuild_secure_urls_image(
                    session, self)

        return {
            'original_filename': self.original_filename,
            'soft_delete': self.soft_delete,
            'url_signed': self.url_signed,
            'annotation_status': self.annotation_status
        }
