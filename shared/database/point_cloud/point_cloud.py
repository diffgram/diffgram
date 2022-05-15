# OPENCORE - ADD
from shared.database.common import *
from shared.settings import settings
from shared.database.common import data_tools


class PointCloud(Base):
    __tablename__ = 'point_cloud'

    id = Column(BIGINT, primary_key = True)

    original_filename = Column(String())
    description = Column(String())
    soft_delete = Column(Boolean, default = False)

    file_list = relationship("File")

    url_signed = Column(String())
    url_signed_blob_path = Column(String())

    url_signed_expiry = Column(Integer)

    url_signed_expiry_force_refresh = Column(Integer)

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    @staticmethod
    def get_by_id(session, id):
        return session.query(PointCloud).filter(PointCloud.id == id).first()

    @staticmethod
    def new(session,
            original_filename = None,
            url_signed_blob_path = None,
            description = None,
            soft_delete = False,
            add_to_session = True,
            flush_session = True
            ):

        point_cloud = PointCloud(
            original_filename = original_filename,
            url_signed_blob_path = url_signed_blob_path,
            description = description,
            soft_delete = soft_delete
        )
        if add_to_session:
            session.add(point_cloud)
        if flush_session:
            session.flush()

        return point_cloud

    def serialize(self, session):

        self.regenerate_url(session)

        point_cloud = {
            'id': self.id,
            'original_filename': self.original_filename,
            'description': self.description,
            'soft_delete': self.soft_delete,
            'url_signed': self.url_signed,
            'url_signed_blob_path': self.url_signed_blob_path,
            'url_signed_expiry_force_refresh': self.url_signed_expiry_force_refresh,
            'time_created': self.time_created,
            'time_updated': self.time_updated,
        }
        return point_cloud

    def regenerate_url(self, session):
        if not self.url_signed_blob_path: return
        should_regenerate, new_offset_in_seconds = data_tools.determine_if_should_regenerate_url(self, session)
        if should_regenerate is True:
            self.url_signed = data_tools.build_secure_url(self.url_signed_blob_path, new_offset_in_seconds)
            self.url_signed_expiry = time.time() + new_offset_in_seconds
            session.add(self)
