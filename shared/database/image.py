from shared.database.common import *

class Image(Base):
    __tablename__ = 'image'

    id = Column(BIGINT, primary_key = True)

    original_filename = Column(String(250))
    description = Column(String(250))
    width = Column(Integer)
    height = Column(Integer)
    rotation_degrees = Column(Integer, default = 0)
    soft_delete = Column(Boolean, default = False)

    mask_joint_url = Column(String())
    mask_joint_blob_name = Column(String())

    is_inference = Column(Boolean, default = False)

    file_list = relationship("File", back_populates="image")

    annotation_status = Column(String())  # "complete" "init" "in_progress" ?

    is_annotation_example = Column(Boolean, default = False)
    url_annotation_example = Column(String())
    url_annotation_example_thumb = Column(String())

    url_public = Column(String())
    url_public_thumb = Column(String())

    url_signed = Column(String())
    url_signed_blob_path = Column(String())

    error = Column(String())

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
            'rotation_degrees': self.rotation_degrees,
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
            'rotation_degrees': self.rotation_degrees,
            'soft_delete': self.soft_delete,
            'url_signed': self.url_signed,
            'url_signed_thumb': self.url_signed_thumb,
            'id': self.id,
            'is_inference': self.is_inference,
            'is_annotation_example': self.is_annotation_example,
            'annotation_status': self.annotation_status
        }
        return image

    def serialize_for_source_control(self,
                                     session = None,
                                     connection_id = None,
                                     bucket_name = None,
                                     reference_file: 'File' = None,
                                     regen_url = True):
        if regen_url:
            from shared.url_generation import blob_regenerate_url
            blob_regenerate_url(blob_object = self,
                                session = session,
                                connection_id = connection_id,
                                bucket_name = bucket_name,
                                reference_file = reference_file)
        return {
            'original_filename': self.original_filename,
            'width': self.width,
            'height': self.height,
            'rotation_degrees': self.rotation_degrees,
            'soft_delete': self.soft_delete,
            'url_signed': self.url_signed,
            'url_signed_thumb': self.url_signed_thumb,
            'error': self.error,
            'url_signed_blob_path': self.url_signed_blob_path,
            'annotation_status': self.annotation_status,
            'id': self.id
        }
