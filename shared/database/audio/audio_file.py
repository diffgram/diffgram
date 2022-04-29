# OPENCORE - ADD
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

    def serialize(self):
        data = self.to_dict(rules = ())

        return data

    def regenerate_url(self, session):
        """
            Refresh signed URL for the raw Audio blob.
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
