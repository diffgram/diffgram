from shared.database.common import *

from sqlalchemy_serializer import SerializerMixin


class AudioFile(Base, SerializerMixin):
    __tablename__ = 'audio_file'

    id = Column(BIGINT, primary_key = True)

    original_filename = Column(String())
    description = Column(String())

    soft_delete = Column(Boolean, default = False)

    url_public = Column(String())

    url_signed = Column(String())
    url_signed_blob_path = Column(String())

    url_signed_expiry = Column(Integer)

    url_signed_expiry_force_refresh = Column(Integer)
    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    @staticmethod
    def get_by_id(session, id):
        return session.query(AudioFile).filter(AudioFile.id == id).first()

    def serialize(self, session, connection_id = None, bucket_name = None, regen_url = True):
        if regen_url:
            from shared.url_generation import blob_regenerate_url
            blob_regenerate_url(blob_object = self,
                                session = session,
                                connection_id = connection_id,
                                bucket_name = bucket_name)

        data = self.to_dict(rules = ())

        return data