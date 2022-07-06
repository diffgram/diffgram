from shared.database.common import *
from shared.database.common import data_tools
from shared.settings import settings
import json
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

    def serialize(self, session, connection_id = None, bucket_name = None):
        self.regenerate_url(session = session)
        data = self.to_dict(rules = ())

        return data

    def regenerate_url(self, session):
        """
            Refresh signed URL for the raw Audio blob.
        :param session:
        :return:
        """
        if not session: return
        if not self.url_signed_blob_path: return

        should_regenerate, new_offset_in_seconds = data_tools.determine_if_should_regenerate_url(self, session)
        if should_regenerate is True:
            self.url_signed = data_tools.build_secure_url(
                self.url_signed_blob_path, new_offset_in_seconds)
            self.url_signed_expiry = time.time() + new_offset_in_seconds
            session.add(self)
