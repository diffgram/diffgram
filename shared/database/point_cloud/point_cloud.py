# OPENCORE - ADD
from shared.database.common import *
from shared.settings import settings
from shared.database.common import data_tools


class PointCloud(Base):
    __tablename__ = 'point_cloud'

    id = Column(BIGINT, primary_key = True)

    original_filename = Column(String(250))
    description = Column(String(250))
    soft_delete = Column(Boolean, default = False)

    file_list = relationship("File")

    url_signed = Column(String())
    url_signed_blob_path = Column(String())

    url_signed_expiry = Column(Integer)

    url_signed_expiry_force_refresh = Column(Integer)

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    def get_by_id(session, id):
        return session.query(PointCloud).filter(PointCloud.id == id).first()

    def serialize(self):

        point_cloud = {
            'id': self.id,
            'original_filename': self.id,
            'description': self.id,
            'soft_delete': self.id,
            'url_signed': self.id,
            'url_signed_blob_path': self.id,
            'url_signed_expiry_force_refresh': self.id,
            'time_created': self.id,
            'time_updated': self.id,
        }
        return point_cloud

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
                self.url_signed_expiry = time.time() + new_offset_in_seconds
                session.add(self)
